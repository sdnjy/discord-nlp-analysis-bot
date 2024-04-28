# discord-analysis
# Overview

This Discord Python bot is designed to analyze conversations within Discord servers. It utilizes Natural Language Processing (NLP) techniques to generate summaries of conversations, extract keywords, and perform sentiment analysis on messages exchanged within Discord channels.

# Commands
## Keywords
Get keywords of the last x messages or the last x minutes. The `channel_name` is Optional.
Example: `/keywords from_last number:2 unit:messages channel_name:general`

## Positivity
Get a sentiment analysis of the last x messages or the last x minutes. The `channel_name` is Optional.
Example: `/positivity from_last number:2 unit:messages channel_name:general`

## Summary
Get a summary of the last x messages or the last x minutes. The `channel_name` is Optional.
Example: `/summary from_last number:2 unit:messages channel_name:general`

## How to setup
- Download and install your models in `models/` folder.
- Put your Discord API token in a `.env` file under the name `DISCORD_TOKEN`

### Locally
Install requirements `pip install -r requirements.txt`

## How to run
### Locally
`python src/bot.py`

### Docker
TBD


## Other prompt ideas
- Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.
- If a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.
    

## TODO
- add docker
- add tests