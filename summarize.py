import argparse
import hashlib
from html.parser import HTMLParser
import json
import math
import os
import random
import requests
import textwrap
import time
import urllib.parse

from alive_progress import alive_bar, alive_it
from dotenv import load_dotenv
from transformers import GPT2TokenizerFast
import openai

load_dotenv()

parser = argparse.ArgumentParser(description='Summarize steam reviews')
parser.add_argument('-a', '--api-key', type=str, help='OpenAI API Key')
parser.add_argument('-t', '--token_limits', type=int, help='Total limit of tokens for a random selection of reviews')
parser.add_argument('-s', '--seed', type=int, help='Seed for random selection of reviews')
parser.add_argument('app_id', type=int, help='Steam App ID (like 2398120)')
args = parser.parse_args()

GPT_MODEL = "gpt-3.5-turbo"
OUTPUT_TOKENS = 600
INPUT_TOKENS_SOFT_MAX = 1000  # optimal input tokens for description
INPUT_TOKENS_HARD_MAX = 3400  # 4000 (max for gpt-3.5-turbo) - 600 (for output tokens)
MAX_TOKENS_PER_REVIEW = 2500
MAX_REVIEWS = 5000

APPROX_COST_PER_TOKEN = 0.000004
APPROX_COST_LIMIT = 0.05
APPROX_TOKENS_PER_MINUTE = 2400

RAW_TO_DESCRIPTION_PROMPT = "Describe (use English) in 500 words all opinions about the game based on game reviews."
RAW_TO_CONCLUSION_PROMPT = "Write a detailed article with an analysis of reviews about the game."
DESCRIPTION_TO_DESCRIPTION_PROMPT = "Combine the descriptions of reviews about the game."
DESCRIPTION_TO_CONCLUSION_PROMPT = "Write a detailed article with an analysis of descriptions of reviews about the game."

SPLITTER = "\n\n---\n\n"
MAX_LEVELS = 10

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

APP_ID = str(args.app_id)
if args.api_key is not None:
    openai.api_key = args.api_key
else:
    openai.api_key = os.getenv("OPENAI_API_KEY")

app_reviews_dir = f"{APP_ID}/reviews"

params_str = str(args.token_limits) + ':' + str(args.seed)
params_hash = hashlib.md5(params_str.encode()).hexdigest()[0:8]
app_texts_dir = f"{APP_ID}/texts/{params_hash}"


def parse_app_info(html_content):
    app_name = None
    is_app_name = False

    def handle_starttag(tag, attrs):
        nonlocal is_app_name
        if tag == 'div' and ('class', 'apphub_AppName') in attrs:
            is_app_name = True

    def handle_data(data):
        nonlocal app_name, is_app_name
        if is_app_name:
            app_name = data.strip()
            is_app_name = False

    parser = HTMLParser()
    parser.handle_starttag = handle_starttag
    parser.handle_data = handle_data
    parser.feed(html_content)

    return {'app_name': app_name}


def get_app_info():
    app_dir = f"{APP_ID}"
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    path_to_app_info = f"{app_dir}/app_info.json"
    if os.path.exists(path_to_app_info):
        with open(path_to_app_info, "r", encoding="utf-8") as f:
            app_info = json.load(f)
            return app_info

    url = f'https://store.steampowered.com/app/{APP_ID}'
    response = requests.get(url)
    app_info = parse_app_info(response.content.decode('utf-8'))
    with open(path_to_app_info, "w", encoding="utf-8") as f:
        json.dump(app_info, f, ensure_ascii=False, indent=4)

    return app_info


def download_reviews():
    something_downloaded = False
    if not os.path.exists(app_reviews_dir):
        os.makedirs(app_reviews_dir)

    last_operation = {
        "cursor": "",
        "batch": 0,
        "downloaded": 0,
        "total": 0,
    }

    if os.path.exists(f"{app_reviews_dir}/last.json"):
        with open(f"{app_reviews_dir}/last.json", "r", encoding="utf-8") as f:
            last_operation = json.load(f)

    url_template = "https://store.steampowered.com/appreviews/{app_id}?json=1&filter=recent&language=all&num_per_page=1000&review_type=all&purchase_type=all&day_range=9999999&start_offset=0&end_offset=0"

    for i in range(0, 2):
        is_first = last_operation["batch"] == 0
        total = 1 if is_first else last_operation["total"]
        if not is_first and last_operation["downloaded"] >= total:
            break

        if not something_downloaded:
            something_downloaded = True
            print("Downloading reviews...")

        with alive_bar(total, bar='blocks' if not is_first else None, spinner='vertical') as bar:
            if not is_first:
                bar(last_operation["downloaded"], skipped=True)
            while True:
                url = url_template.format(app_id=APP_ID)
                if last_operation["cursor"] != "":
                    url += "&cursor=" + urllib.parse.quote_plus(last_operation["cursor"])

                response = requests.get(url)

                if response.status_code == 200:
                    reviews = response.json()
                    num_reviews = reviews["query_summary"]["num_reviews"]
                    last_operation["downloaded"] += num_reviews

                    if "total_reviews" in reviews["query_summary"]:
                        total = reviews["query_summary"]["total_reviews"]
                        if total > MAX_REVIEWS:
                            total = MAX_REVIEWS
                            print(f"Total reviews is more than {MAX_REVIEWS}. Limiting to MAX_REVIEWS={MAX_REVIEWS}.")
                        last_operation["total"] = total

                    if num_reviews == 0:
                        break

                    all_reviews = reviews["reviews"]

                    last_operation["cursor"] = reviews["cursor"]

                    with open(f"{app_reviews_dir}/batch-{last_operation['batch']:03}.json", "w", encoding="utf-8") as f:
                        json.dump(all_reviews, f, ensure_ascii=False, indent=4)

                    last_operation["batch"] += 1

                    with open(f"{app_reviews_dir}/last.json", "w", encoding="utf-8") as f:
                        json.dump(last_operation, f, ensure_ascii=False, indent=4)

                    if is_first:
                        bar(1)
                        break
                    elif last_operation["downloaded"] >= total:
                        bar(num_reviews)
                        break

                    bar(num_reviews)
                else:
                    print(f"Request failed with status code {response.status_code}. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

    if something_downloaded:
        print("Done!")


def select_reviews(token_limit=None, seed=1):
    print("Make a selection of reviews...")
    all_reviews = []
    bar = alive_it(os.listdir(app_reviews_dir), title='Read reviews', bar='blocks', spinner='vertical')
    for filename in bar:
        if filename.startswith("batch-"):
            with open(f"{app_reviews_dir}/{filename}", "r", encoding="utf-8") as f:
                all_reviews.extend(json.load(f))

    total_symbols = 0
    total_tokens = 0
    selected_tokens = 0
    selected_reviews = []

    splitter_tokens = len(tokenizer.encode(SPLITTER))
    print(f"Splitter tokens: {splitter_tokens}")

    if token_limit is not None:
        random.seed(seed)
        random.shuffle(all_reviews)

    if token_limit is not None:
        print(f"Tokenize reviews: selected / limit / total tokens")
    else:
        print(f"Tokenize reviews: selected / total tokens")

    with alive_bar(len(all_reviews), title='Tokenize reviews', bar='blocks', spinner='vertical') as bar:
        for i, review in enumerate(all_reviews):
            bar()
            text = review["review"]
            tokens_count = len(tokenizer.encode(text))
            total_tokens += tokens_count
            total_symbols += len(text)

            bar.text(f'review #{i}: tokens: {tokens_count}, language: {review["language"]}')

            selected = True

            if tokens_count == 0:
                selected = False

            if token_limit is not None and (selected_tokens + tokens_count + splitter_tokens) >= token_limit:
                selected = False

            if tokens_count > MAX_TOKENS_PER_REVIEW:
                selected = False

            if selected:
                selected_reviews.append(text)
                selected_tokens += tokens_count + splitter_tokens

            if token_limit is not None:
                bar.title(f'Tokenize reviews: {selected_tokens} / {token_limit} / {total_tokens}')
            else:
                bar.title(f'Tokenize reviews: {selected_tokens} / {total_tokens}')

    return selected_reviews


def group_texts(texts):
    chunks = []
    current_chunk = ''
    all_text = ''
    for text in texts:
        new_chunk = current_chunk
        if current_chunk != '':
            new_chunk += SPLITTER
        new_chunk += text
        new_chunk_tokens_count = len(tokenizer.encode(new_chunk))
        if new_chunk_tokens_count > INPUT_TOKENS_HARD_MAX:
            chunks.append(current_chunk)
            current_chunk = text
        elif new_chunk_tokens_count > INPUT_TOKENS_SOFT_MAX:
            current_chunk = new_chunk
            chunks.append(current_chunk)
            current_chunk = ''
        else:
            current_chunk = new_chunk

        if all_text != '':
            all_text += SPLITTER
        all_text += text

    if current_chunk != '':
        chunks.append(current_chunk)

    if len(tokenizer.encode(all_text)) <= INPUT_TOKENS_HARD_MAX:
        chunks = [all_text]

    # total tokens count for chunks
    tokens_count = 0
    for chunk in chunks:
        tokens_count += len(tokenizer.encode(chunk))

    return chunks, tokens_count


def describe(texts, level):
    folder = f"{app_texts_dir}/{level}"
    if not os.path.exists(folder):
        os.makedirs(folder)

    prompt = RAW_TO_DESCRIPTION_PROMPT if level == 0 else DESCRIPTION_TO_DESCRIPTION_PROMPT
    title = 'Raw reviews to description' if level == 0 else 'Description to description'

    with alive_bar(len(texts), title=title, bar='bubbles', spinner='dots', stats="(ETA: {eta})") as bar:
        for chunk_index, chunk in enumerate(texts):
            chunk_path = folder + "/" + str(chunk_index) + ".json"

            if os.path.exists(chunk_path):
                bar.text(f'| text #{chunk_index} already analyzed')
                bar(skipped=True)
                continue

            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": chunk},
                ],
                max_tokens=OUTPUT_TOKENS,
            )
            # print(response)
            output = response.choices[0].message.content
            result = {
                'prompt': prompt,
                "input": chunk,
                "output": output
            }

            bar.text(f'| text #{chunk_index} reduced tokens: {len(tokenizer.encode(chunk))} => {len(tokenizer.encode(output))}')

            # save result
            with open(chunk_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            # save text
            with open(chunk_path.replace('.json', '.txt'), "w", encoding="utf-8") as f:
                f.write(output)

            bar()


def load_descriptions(level):
    descriptions = []
    folder = f"{app_texts_dir}/{level}"
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            with open(f"{folder}/{filename}", "r", encoding="utf-8") as f:
                description = json.load(f)
                descriptions.append(description['output'])
    return descriptions


def make_summary(text, from_raw=False):
    if not os.path.exists(app_texts_dir):
        os.makedirs(app_texts_dir)

    summary_path = app_texts_dir + "/summary.json"
    summary_txt_path = app_texts_dir + "/summary.txt"

    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
            return summary['output'], summary_txt_path

    with alive_bar(1, title='Make summary', bar=None, spinner='dots') as bar:
        prompt = RAW_TO_CONCLUSION_PROMPT if from_raw else DESCRIPTION_TO_CONCLUSION_PROMPT
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=OUTPUT_TOKENS,
        )
        # print(response)
        output = response.choices[0].message.content
        result = {
            'prompt': prompt,
            "input": text,
            "output": output
        }
        bar()

    # save result
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    # save txt
    with open(summary_txt_path, "w", encoding="utf-8") as f:
        f.write(output)

    return output, summary_txt_path


def print_summary(summary, filename):
    wrapped_summary = "\n".join(textwrap.wrap(summary, width=100, replace_whitespace=False))
    summary_tokens_count = len(tokenizer.encode(summary))
    title = f' SUMMARY ({summary_tokens_count} tokens) '
    print("{:-^100}".format(title))
    print(wrapped_summary)
    print(f'{"-" * 100}')
    print(f'Summary saved to {filename}')


def confirm():
    while True:
        user_input = input("Do you want to continue? (y/n): ")
        if user_input.lower() == "n":
            print("Exiting the program...")
            return False
        elif user_input.lower() == "y":
            return True
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def main():
    info = get_app_info()
    print(info['app_name'])
    download_reviews()
    reviews = select_reviews(args.token_limits, args.seed if args.seed is not None else 1)
    print(f'Analyze {len(reviews)} reviews')
    current_level = 0
    texts, tokens_count = group_texts(reviews)
    approx_cost = tokens_count * APPROX_COST_PER_TOKEN
    approx_time = math.ceil(tokens_count / APPROX_TOKENS_PER_MINUTE)

    costs = f'The analysis will cost approximately {approx_cost:.3f} USD and take about {approx_time} minutes'
    if approx_cost > APPROX_COST_LIMIT:
        print(f'{costs}. Limit is {APPROX_COST_LIMIT} USD')
        if args.token_limits is None:
            print('Consider using the -t <num> switch to limit the selection of reviews.')
        if not confirm():
            return
    else:
        print(costs)

    if len(texts) > 1:
        print(f'Stage {current_level + 1}. Reviews ({tokens_count} total tokens) grouped into {len(texts)} texts')
        for i in range(MAX_LEVELS):
            describe(texts, current_level)
            descriptions = load_descriptions(i)

            texts, tokens_count = group_texts(descriptions)

            if len(texts) > 1:
                current_level = i + 1
                print(f'Stage {current_level + 1}. Descriptions ({tokens_count} total tokens) grouped into {len(texts)} texts')
            else:
                print(f'Make a summary from descriptions ({tokens_count} total tokens)')
                summary, filename = make_summary(texts[0])
                print_summary(summary, filename)
                break
    else:
        print(f'Make a summary of all reviews ({tokens_count} total tokens)')
        summary, filename = make_summary(texts[0], from_raw=True)
        print_summary(summary, filename)


if __name__ == "__main__":
    main()
