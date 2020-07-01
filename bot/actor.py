import re

import discord
import random
import asyncio
import pprint

import discord
from discord.ext import commands
from pprint import pprint

import checks

from common import cn_id_pattern


def typing_time(msg, seconds_per_char):
    return len(msg) * seconds_per_char


actors = [
    'fang',
    'naomi',
    'naser',
    'rosa',
    'stella',
    'trish',
    'reed',
    'kooper',
    'tester'
]


async def actor_send(cn, msg, delay, typing):
    if delay:
        await asyncio.sleep(delay)

    async with cn.typing():
        await asyncio.sleep(typing)
        await cn.send(msg)


class Actor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        uid = message.author.id
        if uid not in self.bot.config['admin_ids']:
            return

        content = message.content
        if (match := re.match(cn_id_pattern, content)) is None:
            return

        channel_id = int(match.group(1))
        cn = self.bot.guild.get_channel(channel_id)

        if not isinstance(cn, discord.TextChannel):
            await message.channel.send(f'Could not find channel {match}')
            return

        content = content[len(match.group(0)):]
        lines = content.split('\n')

        t = 0
        msg_queue = []

        for line in lines:
            line = line.strip()
            for actor in actors:
                label = f'{actor}:'
                if line.lower().startswith(label):
                    dialog = line[len(label):].strip()
                    mine = actor == self.bot.config["actor"]
                    r = random.uniform(0.8, 1.2)
                    typing = typing_time(dialog, 0.05) * r
                    msg_queue.append((mine, t, typing, dialog))

                    t += typing * 2
                    t += random.uniform(1.25, 2)

        if not msg_queue:
            return

        im_sending = False
        for entry in msg_queue:
            mine, t, typing, dialog = entry
            if mine:
                im_sending = True
                self.bot.loop.create_task(actor_send(cn, dialog, t, typing))

        if im_sending:
            await message.add_reaction('✅')

    # @checks.is_jacob()
    # @commands.command()
    # async def dx(self, ctx):
    #     ns = list(range(1, 4))
    #     for n in ns:
    #         # await actor_send(ctx.channel, str(n) + ' a passing message here', 2, 0.1)
    #         self.bot.loop.create_task(actor_send(ctx.channel, str(n) + ' a passing message here', 2, 0.1))

    # @checks.is_jacob()
    # @commands.command()
    # async def dt(self, ctx, n:int, spc:float):
    #     print('-----')
    #     for i in range(n):
    #         msg = random.choice(samples)
    #         r = random.uniform(0.8, 1.2)
    #         # spc = 0.025
    #         t = min(typing_time(msg, spc) * r, 2.5)
    #         print(msg, len(msg), t, r)
    #         async with ctx.channel.typing():
    #             await asyncio.sleep(t)
    #             await ctx.channel.send(msg) # + f' [{len(msg)}, {spc}, {t}]')
    #         await asyncio.sleep(random.uniform(0.5, 2))
    #     print('====')


def setup(bot):
    actor = Actor(bot)
    bot.add_cog(actor)
    bot.actor = actor
