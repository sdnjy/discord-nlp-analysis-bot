import os
from keybert import KeyBERT
import plotly
import plotly.express as exp
import string
import pandas as pd
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
from collections import Counter
from typing import List, Literal

import discord
from discord import app_commands
from discord.ext import commands

from gpt import run


token = os.getenv("DISCORD_TOKEN")

kw_model = KeyBERT('paraphrase-multilingual-MiniLM-L12-v2')
nltk.download('stopwords')

intents = discord.Intents.default()
intents.message_content = True


description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents, case_insensitive=True)


# Create a Function
async def clean_texts(text):
    """ Function to perform preprocessing """
    
    # Convert to lower cases
    text = text.lower()

    # Exclusion list of punctuations and numbers
    exclist = string.punctuation + string.digits

    
    # # Replace certain words
    # text = text.replace("'", " ").replace("-", " ")
    
    # # Remove punctuations and numbers
    # text = text.translate(str.maketrans("", "", exclist))
    
    # Tokenization
    tokens = word_tokenize(text)
        
    # # Lemmatization
    # tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Remove stop words
    stop_words = stopwords.words('english') + stopwords.words('french')
    tokens = [token for token in tokens if token not in stop_words]
    
    # Join tokens
    clean_text = " ".join(tokens)
    
    # Return the output
    return clean_text


async def get_bert_keywords(text: str):
    text = await clean_texts(text)

    key_words = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        top_n=10,
        highlight=False,
        use_maxsum=True,
        nr_candidates=20,
        stop_words=['french', 'english'])
    return key_words

async def make_summary(text: str):
    model_local_path = (
        # "/home/ayra/dev/discord-analysis/models/orca-mini-3b.ggmlv3.q4_0.bin"
        #"/home/ayra/dev/discord-analysis/models/ggml-model-gpt4all-falcon-q4_0.bin"  # replace with your desired local file path
        "/home/ayra/dev/discord-analysis/models/llama-2-7b-chat.ggmlv3.q4_1.bin"
    )
    #with the important keywords of the sentence in bold
    start_time = time.time()
    summary = await run(model_local_path, prompt_ask="Write me a short and concise summary (no list) about the above text.", text=text)
    time_str = "%.2f" % (time.time() - start_time)
    print(f"Time taken for summary: {time_str}s")
    summary = "**Summary:**\n" + summary
    print(summary)
    return summary

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await bot.change_presence(activity=discord.CustomActivity(name='!get last10msg', emoji='🖥️'))

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise



#@bot.command()
@bot.hybrid_command(description="test")
async def tmp(ctx):
    await ctx.send('Yes, the bot is cool.')



@bot.hybrid_command()
@commands.is_owner()
async def sync(ctx):
    print(f"Sync command: author id {ctx.author.id} with type " + str(type(ctx.author.id)))
    await bot.tree.sync()
    await ctx.send('Command tree synced.')

# @bot.tree.command(guild=TEST_GUILD, description="Submit feedback")
# async def feedback(interaction: discord.Interaction):
#     # Send the modal with an instance of our `Feedback` class
#     # Since modals require an interaction, they cannot be done as a response to a text command.
#     # They can only be done as a response to either an application command or a button press.
#     await interaction.response.send_modal(Feedback())

@bot.hybrid_group() #fallback="all"
async def keywords(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'Command error: !{ctx.subcommand_passed}')


async def get_last_x_msg(channel, number: int = 10):
    msg_list = []
    async for message in channel.history(limit=number, oldest_first=True):
        if message.author.id == bot.user.id:
            continue
        msg_list.append(message.content)

    messages = "\n".join(msg_list)
    return messages

async def get_msg_within_last_x_min(channel, number: int = 10):
    return None

@keywords.command(name="from_last")
async def keywords_from_last(ctx, number: int, unit: Literal['messages', 'minutes']):
    if ctx.author.id == bot.user.id:
        return

    channel = discord.utils.get(bot.get_all_channels(), guild__name='Serveur de arkayra', name="test")
    channel_id = channel.id

    progress_bar = await ctx.reply('=>..', mention_author=True)

    if unit == "messages":
        messages = await get_last_x_msg(channel=channel, number=number)
    else:
        messages = await get_msg_within_last_x_min(channel=channel, number=number)

    # after some things finish
    await progress_bar.edit(content = '==>.')

    keywords = await get_bert_keywords(messages)
    

    # Extract keywords from the KeyBERT output
    df_keywords = pd.DataFrame(keywords, columns=["keyword", "score"])
    fig = exp.bar(df_keywords.sort_values("score", ascending=True), x='keyword', y='score', color="score", color_continuous_scale='Inferno', title="Keywords")

    keywords = df_keywords["keyword"].str.split(" ", expand=True).stack().values
    
    path = "/tmp/keybert.png"
    fig.write_image(path)

    file = discord.File(path, filename="keybert.png")
    embed = discord.Embed(title="Graph")
    embed.set_image(url="attachment://keybert.png")
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.display_avatar.url)
    table_str = "```md\n" + df_keywords.to_markdown() + "```"

    
    
    # after some more things finish
    await progress_bar.edit(content='===>')
    await progress_bar.add_files(file)

    await progress_bar.edit(content=table_str, embed=embed)#, file=file)


@bot.hybrid_group()
async def summary(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')

@summary.command(name="from_last")
async def summary_from_last(ctx, number: int, messages_or_time: Literal['messages', 'minutes']):
    if ctx.author.id == bot.user.id:
        return

    channel = discord.utils.get(bot.get_all_channels(), guild__name='Serveur de arkayra', name="test")

    progress_bar = await ctx.reply('=>..', mention_author=True)

    if messages_or_time == "messages":
        messages = await get_last_x_msg(channel=channel, number=number)
    else:
        messages = await get_msg_within_last_x_min(channel=channel, number=number)

    # after some things finish
    await progress_bar.edit(content = '==>.')

    summary = await make_summary(messages)

    # after some things finish
    await progress_bar.edit(content = '===>')
    await progress_bar.edit(content=summary)

bot.run(token)
