import os
import logging

import discord
from discord.ext import commands

class SentenceAnalysisBot(commands.Bot):
    def __init__(self, **args):
        if "command_prefix" not in args:
            args["command_prefix"] = '!'
        super().__init__(**args)

        # Add more commands
        self.initial_extensions = [
            'cogs.general',
            'cogs.summary',
            'cogs.positivity',
            'cogs.keywords',
        ]

    async def load_extensions(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                # cut off the .py from the file name
                await bot.load_extension(f"cogs.{filename[:-3]}")

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def close(self):
        await super().close()

    # @tasks.loop(minutes=10)
    # async def background_task(self):
    #     print('Running background task...')

    async def on_ready(self):
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
        await self.change_presence(activity=discord.CustomActivity(name='Lurking', emoji='🖥️'))

    async def on_error(event, *args, **kwargs):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.message_content = True
    description = '''I'm a small bot that can do small things like getting keywords and doing summaries'''
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    bot = SentenceAnalysisBot(command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents, case_insensitive=True)
    bot.run(token)