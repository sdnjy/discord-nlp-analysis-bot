import logging
import discord
from discord.ext import commands
from discord.ext.commands import Context

class GeneralCog(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(
        name="ping",
        description="Check if the bot is alive.",
    )
    async def ping(self, context: Context) -> None:
        """
        Check if the bot is alive.

        :param context: The hybrid command context.
        """
        logging.info("Ping")
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"The bot latency is {round(self.bot.latency * 1000)}ms.",
            color=0x9C84EF,
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="sync",
        description="Sync the slash commands",
    )
    @commands.is_owner()
    async def sync(self, ctx: Context):
        logging.info(f"Sync command: author id {ctx.author.id}")
        await self.bot.tree.sync()
        await ctx.send('Command tree synced.')

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCog(bot))