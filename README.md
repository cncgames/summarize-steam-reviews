# Summarize Steam Reviews

## Introduction

The script uses the OpenAI GPT-3.5 model (API key required) to generate summaries of Steam reviews in any language for a given game based on various prompts. It also uses the Steam API (API key not needed) to download the reviews for the game.

You can analyze the entire set of reviews or a random sample.

## How it works

Due to the fact that GPT-3.5 cannot handle more than 4,000 tokens (input+output), the script does the following:

1. The script works by first downloading the reviews for a given game from the Steam API.

2. Then it selects a random sample of reviews or the entire set of reviews.

3. If the number of tokens in the sample is less than 3,400, the script immediately sends it to GPT for summarizing, ending the script.

4. If the number of tokens in the selection is more than 3,400, the script divides the reviews into groups of approximately 1,000 tokens and sends them to GPT to create a description of reviews.

5. After that, the script collects all descriptions and, if the number of tokens is less than 3,400, sends it to GPT to create a summary.

6. If the number of tokens in all intermediate descriptions is greater than 3,400, the script divides the intermediate descriptions and sends them to GPT to create new descriptions.

7. Steps 5 and 6 are repeated until the number of tokens in the intermediate descriptions is less than 3,400.
It then uses the OpenAI API to generate a summary of the reviews.

## Installation

To install the script, follow these steps:

1. Ensure that you have Python 3 installed.
2. Clone or download the repository from GitHub.
3. Install the required packages by running `pip install -r requirements.txt`.
4. Get an OpenAI API key and:
   - Set it to the `OPENAI_API_KEY` environment variable. 
   - Alternatively, you can save `OPENAI_API_KEY` to a `.env` file in the script directory (e.g. `OPENAI_API_KEY=sk-...`).
   - Finally, you can pass the key as a command line argument using `-a` (e.g. `python summarize.py -a sk-...`).
5. You're ready to go!

## Usage

To use the script, follow these steps:

1. Open your terminal or command prompt.
2. Navigate to the directory where the script is located.
3. Run the script by typing `python summarize.py [OPTIONS] <app-id>`.
4. The script will prompt you for any necessary input.
5. The output will be saved to a <app-id> directory.

## Examples

Here are some examples of how to use the script:

### Example 1

Get a summary of all reviews for Command & Control 3 (app-id 1175800).

<details>
<summary>

`python summarize.py 1175800`
</summary>

```commandline
Command & Control 3
Downloading reviews...
1/1 [100%] in 1.6s (0.62/s)
Done!
Make a selection of reviews...
Read reviews |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 2/2 [100%] in 0.1s (19.14/s)
Splitter tokens: 4
Tokenize reviews: selected / total tokens
on 18: Token indices sequence length is longer than the specified maximum sequence length for this model (1368 > 1024). Running this sequence through the model will result in indexing errors
Tokenize reviews: 13476 / 22625 |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 45/45 [100%] in 0.0s (12290.34/s)
Analyze 44 reviews
The analysis will cost approximately 0.054 USD and take about 6 minutes. Limit is 0.05 USD
Consider using the -t <num> switch to limit the selection of reviews.
Do you want to continue? (y/n): y
Stage 1. Reviews (13468 total tokens) grouped into 10 texts
Raw reviews to description <●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●> 10/10 [100%] in 3:11.3 (0.05/s)
Make a summary from descriptions (2797 total tokens)
Make summary 1/1 [100%] in 23.3s (0.04/s)
--------------------------------------- SUMMARY (369 tokens) ---------------------------------------
Additional analysis:

The mixed opinions about Command and Control suggest that the game excels in
some areas, but it fails to meet expectations in others. Many players found the gameplay or
mechanics of the game frustrating, with criticisms ranging from too simplistic or too difficult to
control. One common point of critique is that the AI isn't smart enough or that it becomes too
predictable, leading to repetitive gameplay. On the other hand, it appears that players who enjoy
the game appreciate the ability to try it out for free through a demo and the game's unique and
creative concept.

Another point of comparison worth noting is how different versions of the game
have been received (for example, the Korean-version versus the mobile version). While some reviews
found the Korean version of the game promising due to its unique real-time tactical gameplay and
more customized approach to combat, others found the experience of playing the game to be lacking in
key areas such as unit control and balance.

In the case of Modern Warfare, the game's single-player
campaign is mentioned as one of its standout features, with several reviewers claiming that it has
emotional depth and cinematic qualities. However, some players found the lack of destructible
environments to be disappointing, especially when compared to other similar games such as
Battlefield. The overall consensus seems to be that Modern Warfare offers a solid and immersive
experience, but that there are some areas where it could improve to meet player expectations.

One
significant trend across all of these reviews is the recurring theme of potential. Even negative
reviews of the game often include suggestions on how the game could be improved, indicating that
players see potential in these games and are invested in seeing them develop into better
experiences. Across the board, reviews suggest that developers need to listen to player feedback and
make improvements where necessary to achieve the full potential of their games.
----------------------------------------------------------------------------------------------------
Summary saved to 1175800/texts/2869a5bc/summary.txt
```
</details>

### Example 2

Get a summary of randomized reviews (using seed 123) for Desperados III (app-id 610370), with a maximum budget of 3300 tokens.
<details>
<summary> 

`python summarize.py -t 3300 -s 123 610370`
</summary>

```commandline
Desperados III
Downloading reviews...
on 0: Total reviews is more than 5000. Limiting to MAX_REVIEWS=5000.
1/1 [100%] in 1.7s (0.59/s)
|▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 5000/5000 [100%] in 1:11.3 (67.92/s)
Done!
Make a selection of reviews...
Read reviews |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 51/51 [100%] in 0.1s (481.12/s) 
Splitter tokens: 4
Tokenize reviews: selected / limit / total tokens
on 7: Token indices sequence length is longer than the specified maximum sequence length for this model (1046 > 1024). Running this sequence through the model will result in indexing errors
Tokenize reviews: 3295 / 3300 / 659140 |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 5000/5000 [100%] in 1.2s (4267.17/s)
Analyze 26 reviews
The analysis will cost approximately 0.013 USD and take about 2 minutes
Make a summary of all reviews (3315 total tokens)
Make summary 1/1 [100%] in 27.8s (0.04/s)
--------------------------------------- SUMMARY (444 tokens) ---------------------------------------
Desperados III is a real-time strategy game that takes place in a cowboy-themed world. The game has
received an overall positive response from the players, with many praising its gameplay, mechanics,
and music. The game's developer, Mimimi, is renowned for creating some of the best stealth games in
the world, and Desperados III is no exception.

One of the standout features of the game is its
mechanics, which many reviewers say is similar to the Commandos series. The real-time tactics
gameplay is challenging, but it never gets too frustrating. Players need to use each character's
unique abilities and strengths to solve the game's puzzles and challenges. There are many different
ways to approach each situation, giving players the freedom to discover their own solutions.
Players control up to five characters, each with their own set of skills, including Cooper, who can
throw a knife, climb walls, swim and whistle. Hector is the game's melee character, who can take
down enemies with ease, lay traps and lure enemies towards them.

Many players praised the game for
its challenging levels, which require players to think creatively to succeed. The game is also
highly replayable, with each level offering different paths and options.

The game's music has also
received widespread praise. The soundtrack is atmospheric and fits the game's cowboy theme
perfectly. The graphics are another highlight, with the game's environments and characters well-
designed and detailed.

The game's downside, according to some players, is its perspective. It can
be challenging to see behind buildings or objects, making some actions difficult to execute. The
Showdown mechanic, which pauses the game and allows players to queue up actions, has also received
criticism for being clunky, causing some players to reload their game saves.

In conclusion,
Desperados III is a solid real-time strategy game with excellent mechanics, challenging puzzles, and
engaging characters. The game is highly recommended for fans of the genre, especially those who
enjoy the Commandos series or the developer's previous game, Shadow Tactics: Blades of the Shogun.
Despite a few minor issues, Desperados III is an excellent game well worth playing.
----------------------------------------------------------------------------------------------------
Summary saved to 610370/texts/74334663/summary.txt
```
</details>

### Example 3
Get a summary of randomized reviews (using seed 1) for Cyberpunk 2077 (app-id 1091500), with a maximum budget of 10000 tokens.
<details>
<summary> 

`python summarize.py -t 10000 -s 1 1091500`
</summary>

```commandline
Cyberpunk 2077
Downloading reviews...
on 0: Total reviews is more than 5000. Limiting to MAX_REVIEWS=5000.
1/1 [100%] in 1.9s (0.52/s)
|▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉✗︎ (!) 5099/5000 [102%] in 1:15.6 (65.36/s) 
Done!
Make a selection of reviews...
Read reviews |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 52/52 [100%] in 0.1s (490.92/s) 
Splitter tokens: 4
Tokenize reviews: selected / limit / total tokens
on 53: Token indices sequence length is longer than the specified maximum sequence length for this model (1259 > 1024). Running this sequence through the model will result in indexing errors
Tokenize reviews: 9999 / 10000 / 521254 |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 5099/5099 [100%] in 1.2s (4282.22/s)
Analyze 124 reviews
The analysis will cost approximately 0.040 USD and take about 5 minutes
Stage 1. Reviews (10072 total tokens) grouped into 9 texts
Raw reviews to description <●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●> 9/9 [100%] in 2:21.4 (0.06/s)
Make a summary from descriptions (2396 total tokens)
Make summary 1/1 [100%] in 15.6s (0.06/s)
--------------------------------------- SUMMARY (251 tokens) ---------------------------------------
Opinions about Cyberpunk 2077 are diverse, with both positive and negative reviews. Many
players appreciated the game's visuals, worldbuilding, and attention to detail. They found the story
and characters to be intriguing and engaging, and praised the game's gameplay and customization
options.

However, others were critical of the game's numerous bugs, glitches, and crashes, which
made it unplayable for some. They felt that the game lacked polish, and criticized its performance
on older hardware. Some players described the game as repetitive and formulaic, with few memorable
moments.

Despite these issues, some players still found the game enjoyable in spite of its flaws,
and appreciated its immersion and replayability. They felt that the game's strengths outweighed its
weaknesses, and that the overall experience was worth the investment.

Overall, opinions on
Cyberpunk 2077 are mixed, with some players praising the game for its ambitious storytelling and
immersive world, while others are put off by its technical issues and lack of polish. Ultimately,
whether or not to play the game comes down to the individual's preferences and willingness to
overlook its shortcomings.
----------------------------------------------------------------------------------------------------
Summary saved to 1091500/texts/e67c8946/summary.txt

```
</details>

### Example 4

Get a summary of randomized reviews (using seed 1 by default) for War Mongrels (app-id 1101790), with a maximum budget of 20000 tokens.

<details>
<summary>

`python summarize.py -t 20000 1101790 `
</summary>

```commandline
War Mongrels
Downloading reviews...
1/1 [100%] in 1.8s (0.55/s)
|▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 1297/1297 [100%] in 16.7s (68.25/s)
Done!
Make a selection of reviews...
Read reviews |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 14/14 [100%] in 0.1s (132.43/s) 
Splitter tokens: 4
Tokenize reviews: selected / limit / total tokens
on 45: Token indices sequence length is longer than the specified maximum sequence length for this model (4110 > 1024). Running this sequence through the model will result in indexing errors
Tokenize reviews: 19998 / 20000 / 375259 |▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉| 1297/1297 [100%] in 0.5s (2769.70/s)
Analyze 135 reviews
The analysis will cost approximately 0.080 USD and take about 9 minutes. Limit is 0.05 USD
Do you want to continue? (y/n): y
Stage 1. Reviews (20047 total tokens) grouped into 17 texts
Raw reviews to description <●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●> 17/17 [100%] in 4:53.4 (0.06/s)
Stage 2. Descriptions (4484 total tokens) grouped into 4 texts
Description to description <●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●> 4/4 [100%] in 39.2s (0.09/s)
Make a summary from descriptions (585 total tokens)
Make summary 1/1 [100%] in 15.4s (0.06/s)
--------------------------------------- SUMMARY (268 tokens) ---------------------------------------
Furthermore, some reviewers appreciate the historical context and portrayal of war from multiple
perspectives, while others criticize the game's lack of attention to detail and accuracy. The game's
flaws are not limited to technical issues, as some reviewers suggest that War Mongrels fails to
offer a cohesive narrative and lacks coherent themes. Meanwhile, some compliments for the game
include a genuine sense of dread and tension that works well with the difficult gameplay.

One
aspect of the game that garners mixed reviews is the national narrative. While some viewers praise
the game for granting a unique perspective on the role of different countries during World War II,
others criticize the game's propaganda and glorification of certain nations. Some reviewers suggest
that the game fails to condemn atrocities committed by some sides fully, resulting in a schismatic
and parochial narrative.

In conclusion, the reviews for War Mongrels are a mixed package. Despite
the game's positive attributes like a well-written story, immersive graphics, and gameplay
mechanics, the game's bugs, and glitches are a common issue for players. The game's portrayal of
nationalism and historical context is a contentious issue for some reviewers, but others appreciate
the game's perspective on this issue. Ultimately, the final verdict is up to the players to decide
if they wish to purchase and play the game despite its flaws.
----------------------------------------------------------------------------------------------------
Summary saved to 1101790/texts/468e96d0/summary.txt
```
</details>

## Disclaimer

I don't know English well, and maybe my ChatGPT prompts are not the best. So, if you need to, you can change them as you wish.
