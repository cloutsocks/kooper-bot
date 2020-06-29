import re

import discord
import random

import discord
from discord.ext import commands

import checks

import pronouncing
import syllables
import unidecode

class Mystery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.process_message(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.process_message(after)

    # async def process_message(self, message):
    #     if message.author == self.bot.user:
    #         return
    #
    #     if message.channel.id not in self.bot.config['mystery_channels']:
    #         return
    #
    #     tokens = message.content.split(' ')
    #     last = 0
    #     for w in tokens:
    #         n = self.syllable_count(w)
    #         if n < last:
    #             try:
    #                 await message.delete()
    #             except Exception:
    #                 pass
    #             return
    #         last = n

    async def process_message(self, message):
        if message.author == self.bot.user:
            return

        if message.channel.id not in self.bot.config['mystery_channels']:
            return

        tokens = message.content.split(' ')
        last = 0
        passed = True
        m = []
        for w in tokens:
            n = self.syllable_count(w)
            if n < last:
                passed = False
            last = n
            m.append(f'{w} ({n})')
        msg = ' '.join(m)
        if msg:
            status = '✅' if passed else '❌'
            msg = f'{msg} {status}'
            await message.channel.send(msg)

    def syllable_count(self, w):
        word = unidecode.unidecode(w.lower())
        pronunciation_list = pronouncing.phones_for_word(word)
        if not pronunciation_list:
            return syllables.estimate(word)
        return pronouncing.syllable_count(pronunciation_list[0])

def setup(bot):
    mystery = Mystery(bot)
    bot.add_cog(mystery)
    bot.mystery = mystery
