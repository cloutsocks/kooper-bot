import discord
from discord.ext import commands

import checks

__ = '    \u200b'
ARROW = '<:arrow:745744683040243782>'

class Jam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_jacob()
    @commands.command()
    async def jam(self, ctx):
        session = JamSession(self.bot, ctx.author)
        await session.send_initial_prompt(ctx)

    @checks.is_jacob()
    @commands.command()
    async def how(self, ctx):
        e = discord.Embed(title="how 2 jam", color=0x57AADE)
        e.description = help_text
        await ctx.send(embed=e)

def melody_as_text(melody, ticks):
    if not melody:
        return 'None'

    chunks = [f'`{melody[i:i + ticks]}`' for i in range(0, len(melody), ticks)]
    return f"{' '.join(chunks)}"


class JamSession(object):
    def __init__(self, bot, member):
        self.bot = bot
        self.member = member
        self.bpm = 90
        self.ticks = 4
        self.embed = None
        self.lead = 'DCBCD---B-B-B--C'
        self.drums = None
        self.wfr_message = None

    async def send_initial_prompt(self, ctx):
        e = self.make_embed()
        self.wfr_message = await ctx.send(embed=e)
        reactions = ['❓', '🎸', '🥁', '⏯', '❌']
        for reaction in reactions:
            await self.wfr_message.add_reaction(reaction.strip('<>'))
            self.bot.wfr[self.member.id] = self

    def make_embed(self):
        desc = '''we're gonna make a song right here, right now. cool, right?
        
click an instrument or ❓ if you need some help!'''

        e = discord.Embed(title="let's jam!", color=0x57AADE)
        e.description = desc

        e.add_field(name=f'🕗 BPM', value=f'{self.bpm}', inline=True)
        e.add_field(name=f'🎼 Ticks', value=f'{self.ticks} per bar', inline=True)
        e.add_field(name=f'🎸 Lead', value=melody_as_text(self.lead, self.ticks), inline=False)
        e.add_field(name=f'🥁 Drums', value=melody_as_text(self.drums, self.ticks), inline=False)

        return e


def setup(bot):
    jam = Jam(bot)
    bot.add_cog(jam)
    bot.jam = jam


help_text = f'''ok! so while we're jamming,

{ARROW} type any number between 60 and 140 to change the **bpm** - how fast we're playing!

{ARROW} type any number between 1 and 8 to change how many **ticks** are in a bar. doubling from 4 to 8 lets us go wild with drums. more ticks = more drums!

⏯ click this to record and play back your tune!

got it? if not, maybe a friend here can help!
'''