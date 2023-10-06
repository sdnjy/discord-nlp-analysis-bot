from datetime import datetime, timezone, timedelta

import re
import logging
import discord
from discord.ext import commands
from typing import Literal

async def get_last_x_msg(bot: commands.Bot, channel: discord.TextChannel, number: int = 10) -> str:
    msg_list = []
    async for message in channel.history(limit=number, oldest_first=False):
        if message.author.id == bot.user.id:
            continue
        author_message = f"{message.author.display_name}: {message.content}"
        msg_list.append(author_message)
    
    messages = "\n".join(msg_list[::-1])
    return messages

async def get_msg_within_last_x_min(bot: commands.Bot, channel: discord.TextChannel, number: int = 10) -> str:
    msg_list = []
    after_time = datetime.now(timezone.utc) - timedelta(minutes=number)
    async for message in channel.history(limit=4000, after=after_time):
        if message.author.id == bot.user.id:
            continue
        author_message = f"{message.author.display_name}: {message.content}"
        msg_list.append(author_message)

    messages = "\n".join(msg_list[::-1])
    return messages

async def preprocess_text(text: str) -> str:
    """Keeps only letters and numbers"""
    text = re.sub("(<:[A-Za-z0-9]*:\d*>)", "", text)
    
    # TODO: convert emojis and discord emojis to text 
    
    return str(text)

async def get_channel(bot: commands.Bot, ctx: commands.Context, channel_name: str | None):
    if channel_name is None:
        channel = ctx.message.channel

    # <#1139964453031510018> case
    elif re.search("^<#\d*>$", channel_name):
        channel_id = channel_name[len('<#'):-len('>')]
        logging.debug(f"channel_id {channel_id}")
        channel = discord.utils.get(bot.get_all_channels(), id=int(channel_id))

    else:
        if len(channel_name) > 0 and channel_name[0] == '#':
            channel_name = channel_name[1:]
        channel = discord.utils.get(bot.get_all_channels(), name=channel_name)
    return channel

async def get_discord_last_messages(
        bot: commands.Bot,
        ctx: commands.Context,
        channel_name: str | None,
        number: int,
        unit: Literal['messages', 'minutes']
    ) -> str:
    logging.info(f"get_discord_last_messages channel {channel_name}, last {number} {unit}")
    channel = await get_channel(bot, ctx, channel_name)

    logging.info("Getting last messages")
    if unit == "messages":
        messages = await get_last_x_msg(bot=bot, channel=channel, number=number)
    else:
        messages = await get_msg_within_last_x_min(bot=bot, channel=channel, number=number)
    messages = await preprocess_text(messages)

    logging.debug(f"get_discord_last_messages: {messages}")
    return messages