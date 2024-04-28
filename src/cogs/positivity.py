import time
import os
from discord.ext import commands
from typing import Literal
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from typing import Dict
import logging

from utils.discord_utils import get_discord_last_messages

class PositivityCog(commands.Cog):
    _hugging_face_models = {
        "distilbert_multilingual": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        "bert_multilingual_uncased": "nlptown/bert-base-multilingual-uncased-sentiment",
        "sentiment-analysis": "sentiment-analysis",
        
    }

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        nltk.download('vader_lexicon')

    @commands.hybrid_group(name="positivity")
    async def positivity(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No, {ctx.subcommand_passed} is missing arguments')

    async def _sentiment_dict_to_str(self, sentiment_dict: Dict[str, float]) -> str:
        """Format prettily the sentiments results
        Example of sentiment_dict:
        sentiment_dict = {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
        """
        translation_dict = {
            "neg": "negative",
            "neu": "neutral",
            "pos": "positive",
        }
        sentiment_string = "**Sentiment:**"
        for sentiment, sentiment_score in sentiment_dict.items():
            if sentiment == "compound":
                continue
            if sentiment_score >= 0.2:
                sentiment_string += " " + str(int(sentiment_score * 100)) + "% " + translation_dict[sentiment]
        return sentiment_string


    async def hugging_face_sentiment_analysis(self, text: str):
        """huggingface models sentiment analysis
        Can use any model in self._hugging_face_models 

        Args:
            text (str): the text to classify

        Returns:
            str: the classification (positive or negative) of the text
        """
        sentiment_pipeline = pipeline(model=self._hugging_face_models["distilbert_multilingual"])
        return sentiment_pipeline(text)
    
    async def nltk_sentiment_analysis(self, text: str):
        sia = SentimentIntensityAnalyzer()
        sentiment_dict = sia.polarity_scores(text)
        return await self._sentiment_dict_to_str(sentiment_dict)


    async def _get_sentiment_analysis(self, text: str):
        """Gets the sentiment analysis (positive, negative, neutral) from a text
        Can use NLTK or Hugging face models
        self.nltk_sentiment_analysis or self.hugging_face_sentiment_analysis
        """
        logging.debug(f"text: {text}")
        start_time = time.time()
        
        sentiment = await self.nltk_sentiment_analysis(text)

        time_str = "%.2f" % (time.time() - start_time)
        logging.info(f"Time taken for sentiment analysis: {time_str}s")

        return sentiment

    @positivity.command(
        name="from_last",
        description="Get the sentiment analysis from the last x minutes/messages")
    async def sub_command(self, ctx: commands.Context, number: int, unit: Literal['messages', 'minutes'], channel_name: str = None) -> None:
        logging.info("Sub command 'sentiment analysis' received")
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

        logging.info("Computing sentiment analysis")
        await progress_bar.edit(content = '==>.')
        sentiment_analysis = "No messages found"
        if len(messages) > 0:
            sentiment_analysis = await self._get_sentiment_analysis(messages)

        # after some things finish
        await progress_bar.edit(content = '===>')
        await progress_bar.edit(content=sentiment_analysis)
        logging.info("Sub command 'sentiment analysis' finished")

    
async def setup(bot: commands.Bot):
  await bot.add_cog(PositivityCog(bot))