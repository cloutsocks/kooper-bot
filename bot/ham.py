import asyncio
import copy
import math
import random
import json
import os
import io
import subprocess
import time

import discord
from discord.ext import commands

import checks, re

from PIL import Image, ImageDraw, ImageFont, ImageColor

from common import send_message, cn_id_pattern

__ = '    \u200b'
ARROW = '<:arrow:745744683040243782>'
DEFAULT = 'hamtaro_000'

HELP_MSG = '''`.ham <name> <emotion> <text goes here>`
`<emotion>` can be a word (`blush`) or number (1 = smile, 6 = frown)
single sprite hams don't need an emotion

type `.hams` for list of hams'''


HELP_HAMS = '''`.ham <name> <emotion> <text goes here>`
`<emotion>` is optional and can be a word (`blush`) or number (1 = smile, 6 = frown)
if omitted, first emotion is used
single sprite hams don't need an emotion

**characters**

base emotions [1-10]: `smile` `smilesweat` `happy` `happysweat` `happycry` `frown` `frownsweat` `worry` `worrysweat` `cry`

hamtaro: [base] `flatsweat` `flatsweat_worry` `ohno`
boss: [base] `blush` `blush_sweat` `sob`
oxnard: [base] `sparkle` `blush` `sob`
bijou: [base] `blush` `happyblush` `wink` `ranger`
pashmina: [base] `content` `ranger`
penelope: [base] `sob` `ranger`
howdy: [base] `costume` `ranger`
dexter: [base] `eyesshut` `eyesshutworry` `eyesshutsweat`
stan: [base] `eyesshut` `eyesshutworry` `eyesshutsweat`
maxwell: [base] `blush` `pointsweat` `point` `eyesshut` `eyesshutsweat` `winkleft` `winkright`
sandy: [base] `blush` `blushcry` `tiredsweat` `back` `hold` `sad2` `happy2` `beam` `ranger`
cappy: [base]
panda: [base]
princebo: [base] `sparkle` `sob`
jingle: `smile` `happy` `happy2` `point` `eyesshut`
sailor: `green` `blue` `mint` `yellow`


**single sprite**
_(no emotion needed)_

snoozer, elder, championi, radar, marron, king, bronze, silver, lawyer, glasses, magician, omar, sparkle, drpeanut, seedric, announcer, carrobo, ice, lolly, tux, salia, postie, nerd, seamore, oshare, flora, ookook, sabu, stucky, auntieviv, tomyt, eggyp, sheriff, police, judo, ghost, news, girl, solara, angy, farmer, snorker, yell


_for a list of generic colored/striped hamsters, type `.hams2`_'''

HELP_HAMS2 = '''`.ham <name> <emotion> <text goes here>`
`<emotion>` can be a word (`blush`) or number (1 = smile, 6 = frown)
single sprite hams don't need an emotion

**generics**

hamster: `gray` `orange` `mint` `brownpattern` `bluepattern` `ltbrownpattern` `greenpattern` `purplepattern` `purpleears` `yellowears` `pink` `cream` `dkorange` `violetpattern` `mintpattern` `pinkpattern` `rosepattern` `pinkbrownpattern` `pinkears` `mintears` `pigtails` `afro` `yellowbeard` `graybeard` `bluepattern2`

round: `mint` `white` `brown` `brownpattern` `yellowpattern` `purplepattern` `bluepattern` `mosspattern` `pinkears` `whiteears` `violet` `green` `orange` `greenpattern` `ltbrownpattern` `graypattern` `dkbrownpattern` `orangepattern` `brownears` `blueears` `greyfrown` `greysad`

small: `orange` `green` `brown` `orangepattern` `purplepattern` `brownpattern` `bluepattern` `yellowpattern` `greenears` `brownears` `white` `pink` `blue` `violetpattern` `greenpattern` `cyanpattern` `pinkpattern` `whitepattern` `orangeears` `pinkblack`

old: `blue` `green` `orangepattern` `bluepattern` `brownpattern` `greenpattern` `yellowpattern` `blueears` `greenears`

'''


class Ham(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.render = Render()

    @commands.command()
    async def hams(self, ctx):
        e = discord.Embed(description=HELP_HAMS)
        e.set_image(url='https://i.imgur.com/WUVjWqb.png')
        await ctx.send(embed=e)

    @commands.command()
    async def hams2(self, ctx):
        e = discord.Embed(description=HELP_HAMS2)
        e.set_image(url='https://i.imgur.com/WUVjWqb.png')
        await ctx.send(embed=e)

    def replace_channel_mentions(self, m):
        channel_id = int(m.group(1))
        channel = self.bot.get_channel(channel_id)

        if not isinstance(channel, discord.TextChannel):
            return m.group(0)

        return '*#' + channel.name + '*'

    @commands.command(aliases=['hamtaro'])
    async def ham(self, ctx, *, arg=''):

        try:
            first, rest = arg.split(' ', 1)
        except ValueError:
            await send_message(ctx, HELP_MSG, error=True)
            return

        cid = None
        cn = None
        match = cn_id_pattern.search(first)
        if match:
            cid = int(match.group(1))
        else:
            try:
                cid = int(first)
            except ValueError:
                pass

        if not cid:
            rest = arg
        else:
            cn = self.bot.get_channel(cid)

            if not isinstance(cn, discord.TextChannel):
                await ctx.send(f'Could not find channel {match}')
                return

        try:
            name, rest = rest.split(' ', 1)
        except ValueError:
            await send_message(ctx, HELP_MSG, error=True)
            return

        if ' ' in rest:
            emotion, text = rest.split(' ', 1)

            if emotion not in self.render.emotions:
                text = emotion + ' ' + text
                emotion = 1
        else:
            emotion = 1
            text = rest

        text = cn_id_pattern.sub(self.replace_channel_mentions, text)

        # try:
        #     name, emotion, text = rest.split(' ', 2)
        # except ValueError:
        #     await send_message(ctx, HELP_MSG, error=True)
        #     return

        png = self.render.render(text, name, emotion)

        msg = ''
        if cn is not None and ctx.author.guild_permissions.manage_guild:
            msg = '🐸 **staff message**'
            await ctx.message.add_reaction('✅')
        else:
            msg = f'{ctx.author.display_name}:'
            await ctx.message.delete()
            cn = ctx

        await cn.trigger_typing()
        await cn.send(msg, file=discord.File(fp=png, filename='ham.png'))


color_toggle = ['*', '_s']

class Render:
    def __init__(self):
        self.atlas = Image.open('ham/hrr-font.png').convert('RGBA')
        self.canvas = Image.open('ham/hrr-blank.png').convert('RGBA')

        self.map = {}
        self.names = []
        self.emotions = []

        with open('ham/hrr.json') as f:
            self.data = json.load(f)

        self.make_map()

    def make_map(self):
        f = open('ham/map.csv', 'r', encoding='utf-8')
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.split(',')
            try:
                key = parts[0]
                name = parts[1].replace('_', '')
                emotion = parts[2].replace('_', '')
            except IndexError:
                continue
                
            if not name or name == '-' or emotion == '-':
                continue

            if not emotion:
                emotion = 'default'

            if name not in self.map:
                self.map[name] = {}

            self.names.append(name)
            self.emotions.append(emotion)
            self.map[name][emotion] = key

        f.close()

        self.names = list(set(self.names))
        self.emotions = list(set(self.emotions))

    def find_key(self, name, emotion):
        if name not in self.map:
            return DEFAULT

        hamster = self.map[name]

        if isinstance(emotion, int):
            a = list(hamster)
            try:
                return hamster[a[emotion]]
            except IndexError:
                return hamster[a[0]]

        if emotion not in hamster:
            return hamster[next(iter(hamster))]

        return hamster[emotion]

    def render(self, text, name=None, emotion=None):
        if name:
            name = name.lower().strip().replace('_', '')

        if emotion:
            try:
                emotion = int(emotion) - 1
            except ValueError:
                emotion = emotion.lower().strip().replace('_', '').replace('grey', 'gray')

        key = self.find_key(name, emotion)
        return self.render_with_key(text, key)

    def render_with_key(self, text, key=DEFAULT):
        data = self.data
        portraits = data['overlays']['portait']['options']
        offsets = data['shiftfonts']

        canvas = self.canvas.copy()

        h = 12  # data['height']

        sox, soy = 0, 0

        # portrait

        p = portraits[key]
        px = p['x']
        py = p['y']
        pw = p['w']
        ph = p['h']

        portrait = self.atlas.crop((px, py, px + pw, py + ph))
        canvas.paste(portrait, (0, 0, pw, ph), portrait)

        # text

        tox, toy = data['origin']['x'], data['origin']['y']
        tx, ty = tox, toy
        wrap_width = tox + int(data['wrap-width'])
        color = False
        for word in text.split(' '):

            word_width = 0
            for c in word:
                key = str(ord(c))
                if key not in data:
                    continue

                word_width += data[key]['w']

            if tx + word_width > wrap_width:
                tx = tox
                ty += 13

            for c in word + ' ':

                if c in color_toggle:
                    color = not color
                    continue

                key = str(ord(c))
                if key not in data:
                    continue

                sx = sox + data[key]['x']
                sy = soy
                if color:
                    sy += offsets['pink']

                w = data[key]['w']

                if tx + w > wrap_width:
                    tx = tox
                    ty += 13

                letter = self.atlas.crop((sx, sy, sx + w, sy + h))
                canvas.paste(letter, (tx, ty, tx + w, ty + h), letter)

                tx += w

        canvas = canvas.resize((480, 128), Image.NEAREST)

        png = io.BytesIO()
        canvas.save(png, format='PNG', optimize=False)
        png.seek(0)
        return png

    def make_ham_guide(self):

        data = self.data
        portraits = data['overlays']['portait']['options']

        sizew = 90
        sizeh = 95
        columns = 11
        rows = 7

        tox, toy = 0, 74
        pox, poy = int((sizew - 64) / 2), 10


        canvas = Image.new('RGBA', (sizew * columns, sizeh * rows), 'white')
        for i, name in enumerate(self.map):
            emotion = list(self.map[name])[0]
            key = self.map[name][emotion]

            p = portraits[key]
            px = p['x']
            py = p['y']
            pw = p['w']
            ph = p['h']

            portrait = self.atlas.crop((px, py, px + pw, py + ph))
            # canvas.paste(portrait, (0, 0, pw, ph), portrait)

            canvas.paste(portrait, (pox + i % columns * sizew, poy + int(i / columns) * sizeh), portrait)

            tx, ty = 0, 0

            tx = int(pox + 64 / 2 - 6 * len(name) / 2)

            # int(0 - 6 * len(name) / 6)

            for c in name:
                key = str(ord(c))
                if key not in data:
                    continue

                sx = data[key]['x']
                sy = i % 7 * 12 #data['shiftfonts']['pink']
                w = data[key]['w']
                h = 12

                letter = self.atlas.crop((sx, sy, sx + w, sy + h))
                # canvas.paste(letter, (tx, ty, tx + w, ty + h), letter)

                canvas.paste(letter, (tox + i % columns * sizew + tx, toy + int(i / columns) * sizeh + ty), letter)

                tx += w

        # canvas = canvas.resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
        canvas.save('ham/test/guide.png')



def setup(bot):
    ham = Ham(bot)
    bot.add_cog(ham)
    bot.ham = ham


# render = Render()
# render.make_ham_guide()


# for name in ['hamster', 'round', 'small', 'old']:
#     keys = list(key for key in render.map[name])
#     keys = ' '.join([f'`{key}`' for key in keys])
#     print(f'{name}: {keys}')


# print(render.map)
# print(render.find_key('hamster', 1))

# render.render('but what if we added the *ham-hams* to the *server* aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffdddddddddddddd')