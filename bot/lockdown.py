import asyncio
import re

import discord
import random

from datetime import datetime, timedelta

import discord
from discord.ext import commands
from common import whois_text, find_members, send_message, get_member_or_search, idPattern, DBL_BREAK, FIELD_BREAK

import checks

# unlock procedure:
# iterate over provided categories
# alter category permission
# iterate channels within category
# if synced, ignore, else alter category permission
# alter logic: if everyone set to view false and role set to view, set everyone to /
# change channel name if it exists

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    async def on_load(self):
        pass