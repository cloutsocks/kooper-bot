import time
import random
from collections import namedtuple

import aiohttp
import discord
import pprint

import checks

from discord.ext import commands

from common import send_message, DBL_BREAK

CardRecord = namedtuple('CardRecord',
                        'discord_id, discord_name, fc, ign, switch_name, title_1, title_2, pkmn_icon, color, img, quote')


class Students(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''
    id
    '''

    @checks.is_jacob()
    @commands.command()
    async def id(self, ctx, *, arg=''):
        if not arg:
            await self.view_card(ctx)
            return

        # helpMsg = '''TODO help menu'''
        # mention = resolve_mention(ctx.message.guild, arg)
        # if mention:
        #     await self.view_card(ctx, mention)
        #     return
        #
        # await send_message(ctx, f'''Couldn\'t find that user!{DBL_BREAK}{helpMsg}''', error=True)

    async def view_card(self, ctx, member=None):
        member = member or ctx.author

        # await ctx.trigger_typing()

        TYPE_COLORS = (
            0xFFFFFF,
            0xE88158,
            0x57AADE,
            0x7FBF78,
            0x9C6E5A,
            0xF2CB6F,
            0x9DD1F2,
            0xAD70D5,
            0xF0A1C1,
            0x222222,
            0x646EAB
        )

        ROLE_COLORS = (
            # 🍂 Autumn
            0xffb88c,

            # 🍎 Red Apple
            0xff9999,

            # 🍒 Cherries
            0xff6063,

            # 🍓 Strawberry
            0xfcbad3,

            # 🌸 Cherry Blossom
            0xf0cafc,

            # 🌷 Lilac
            0xa991e8,

            # 🌠 Midnight
            0x6772e5,

            # ⛅ Blue Skies
            0x99ccff,

            # 🌿 Bluegrass
            0x38b2a5,

            # 🌱 Baby Mint
            0x99ffdc,

            # 🌲 Evergreen
            0x62d2a2,

            # 🍃 Spearmint
            0x82ffb0,

            # 🍌 Banana
            0xffe676,

            # 🐝 Bumblebee
            0xffdd99,

            # 🌻 Sunflower
            0xffbb42,

            # 🍊 Tangerine
            0xff9e42,

            # ☕ Espresso
            0x9c6343,

            # 🍫 Pain au Chocolat
            0x8d6262,

            # 🌙 Night
            0x000000
        )

        name = str(member)
        img = 'https://i.imgur.com/KR8bold.png'
        color = random.choice(ROLE_COLORS)
        footer = '🦕 Volcano High Student ID'
        clubs = '''<@&729836963116482641>
<@&729836974785036419>
<@&729836973547716669>'''

        description = '''_stay-at-home frog_
🌸 he/him ┊ 🌿 Herbivore ┊ 🎂  May 23\n\u200b'''

        # .set_image(url=img) \

        __ = '    \u200b'

        e = discord.Embed(title=member.name, description=description, color=color) \
            .add_field(name=f'🎭 Clubs{__}', value=clubs, inline=True) \
            .add_field(name=f'🎨 Society{__}', value='???', inline=True) \
            .add_field(name=f'🎼 Signature Tune{__}', value='_Secret of Mana_\n[E+A+ G+C+ D+DE A+--](https://nooknet.net/tunes?t=008558ca2b4a5db6)', inline=True) \
            .set_footer(text=footer)

        # .set_image(url='https://i.imgur.com/d9fpjkN.png') \

        await ctx.send(f'<@{ctx.author.id}>', embed=e)



def setup(bot):
    students = Students(bot)
    bot.add_cog(students)
    bot.students = students
