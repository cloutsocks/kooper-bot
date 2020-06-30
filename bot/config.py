import re

import discord
import random
import os
import discord
import json
from discord.ext import commands

import checks


def load_config(bot):
    with open(os.environ.get('CONFIG_PATH', '../config/config_kooper.json')) as f:
        bot.config = json.load(f)

        for key in ['creator_ids', 'admin_ids']:
            bot.config[key] = [int(val) for val in bot.config[key]]


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_config(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        load_config(self.bot)


def setup(bot):
    config_cog = Config(bot)
    bot.add_cog(config_cog)
