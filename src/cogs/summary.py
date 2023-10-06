import time
import os
from discord.ext import commands
from typing import Literal
import logging

from utils.gpt import gpt_pipeline_predict
from utils.discord_utils import get_discord_last_messages

class SummaryCog(commands.Cog):
    _models_path = "models/"
    _models_files = {
        "orca": "orca-mini-3b.ggmlv3.q4_0.bin",
        "falcon": "ggml-model-gpt4all-falcon-q4_0.bin",
        "llama": "llama-2-7b-chat.ggmlv3.q4_1.bin",
    }

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="summary")
    async def summary(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


    async def _make_summary(self, text: str):
        model_local_path = os.path.join(self._models_path, self._models_files["llama"])
        
        start_time = time.time()
        logging.info(f"Input text: {text}")
        summary = await gpt_pipeline_predict(model_local_path, prompt_ask="Write me a short and concise summary.", text=text)
        time_str = "%.2f" % (time.time() - start_time)
        logging.info(f"Time taken for summary: {time_str}s")
        summary = "**Summary:**\n" + summary
        logging.info(summary)
        return summary

    @summary.command(
        name="from_last",
        description="Get the summary from the last x minutes/messages")
    async def sub_command(self, ctx: commands.Context, number: int, unit: Literal['messages', 'minutes'], channel_name: str = None) -> None:
        logging.info("Sub command 'summary' received")
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

        logging.info("Computing summary")
        await progress_bar.edit(content = '==>.')
        summary = await self._make_summary(messages)

        # Sending to discord the content
        await progress_bar.edit(content = '===>')
        await progress_bar.edit(content=summary)
        logging.info("Sub command 'summary' finished")

    
async def setup(bot: commands.Bot):
  await bot.add_cog(SummaryCog(bot))