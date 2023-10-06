import pandas as pd
import plotly.express as exp
import string
import nltk
import logging
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from keybert import KeyBERT

import discord
from discord.ext import commands
from typing import Literal

from utils.discord_utils import get_discord_last_messages

class KeywordsCog(commands.Cog):
    _keybert_models = {
        "multilingual" : "paraphrase-multilingual-MiniLM-L12-v2"
    }

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.kw_model = KeyBERT(self._keybert_models["multilingual"])
        nltk.download('stopwords')

    @commands.hybrid_group(name="keywords")
    async def keywords(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No, {ctx.subcommand_passed} is missing arguments')

    # Create a Function
    async def clean_texts(self, text):
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
        tokens = [token for token in tokens if token not in stop_words and token not in exclist]
        
        # Join tokens
        clean_text = " ".join(tokens)
        
        # Return the output
        return clean_text

    async def get_bert_keywords(self, text: str):
        text = await self.clean_texts(text)

        key_words = self.kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),
            top_n=10,
            highlight=False,
            use_maxsum=True,
            nr_candidates=20,
            stop_words=['french', 'english'])
        return key_words

    @keywords.command(
        name="from_last",
        description="Get the keywords from the last x minutes/messages",
    )
    async def sub_command(self, ctx: commands.Context, number: int, unit: Literal['messages', 'minutes'], channel_name: str = None) -> None:
        logging.info("Sub command 'keywords' received")
        if ctx.author.id == self.bot.user.id:
            return
        
        progress_bar = await ctx.reply('=>..', mention_author=True)
        messages = await get_discord_last_messages(
            self.bot,
            ctx=ctx,
            channel_name=channel_name,
            number=number,
            unit=unit,
        )

        logging.info("Computing the keywords")
        await progress_bar.edit(content = '==>.')
        keywords = await self.get_bert_keywords(messages)
        

        # Extract keywords from the KeyBERT output
        logging.info("Making graphs and stats")
        df_keywords = pd.DataFrame(keywords, columns=["keyword", "score"])
        fig = exp.bar(df_keywords.sort_values("score", ascending=True), x='keyword', y='score', color="score", color_continuous_scale='Inferno', title="Keywords")

        keywords = df_keywords["keyword"].str.split(" ", expand=True).stack().values
        
        path = "/tmp/keybert.png"
        fig.write_image(path)

        file = discord.File(path, filename="keybert.png")
        embed = discord.Embed(title="Graph")
        embed.set_image(url="attachment://keybert.png")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.display_avatar.url)
        table_str = "```md\n" + df_keywords.to_markdown() + "```"

        
        await progress_bar.edit(content='===>')
        await progress_bar.add_files(file)

        await progress_bar.edit(content=table_str, embed=embed)#, file=file)
        logging.info("Sub command 'keywords' finished")

    
async def setup(bot: commands.Bot):
  await bot.add_cog(KeywordsCog(bot))