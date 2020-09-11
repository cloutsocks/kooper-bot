import asyncio
import random
import re
import os
import subprocess

import discord
from discord.ext import commands

from datetime import datetime, timedelta
from common import send_message, idPattern, get_member_or_search, emojiPattern, customEmojiPattern, simplify_timedelta

import checks

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pets = 0
        self.max_pets = random.randint(5, 420)

    async def remove_raw_reaction(self, payload, user=None):
        if not user:
            user = self.bot.get_user(payload.user_id)
            if not user:
                return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction(payload.emoji, user)

    async def add_roles_to_every_poster(self, channel_id, role_id):

        channel = self.bot.get_channel(channel_id)
        role = channel.guild.get_role(role_id)

        # for member in role.members:
        #     print(f"Remove for {member}")
        #     await member.remove_roles(role)

        async for message in channel.history(limit=None):
            if message.author in channel.guild.members:
                print(f'Adding to {message.author}')
                await message.author.add_roles(role)
            else:
                print(f'Not in guild, deleting {message.author}')
                await message.delete()


    @checks.is_mod()
    @commands.command()
    async def say(self, ctx, channel:discord.TextChannel, *, arg):
        await channel.send(arg)
        await ctx.message.add_reaction('✅')

    @checks.is_mod()
    async def repeat(self, ctx, *, arg):
        await ctx.send(arg)

    @checks.is_mod()
    @commands.command(name='embed')
    async def repeat_embed(self, ctx, *, arg):
        await ctx.send(embed=discord.Embed(description=arg))

    # @checks.is_mod()
    # @commands.command()
    # async def naomi(self, ctx, channel:discord.TextChannel, *, arg):
    #     await channel.send(arg)
    #     await ctx.message.add_reaction('✅')

    @checks.is_mod()
    @commands.command(aliases=['dm'])
    async def msg(self, ctx, *, arg):

        try:
            query, msg = arg.split(' ', 1)
        except ValueError:
            await send_message(ctx, 'Please include a message to send with. Usage: `.msg <member query> <msg>', error=True)
            return

        success, result = await get_member_or_search(self.bot, ctx.message.guild, query)
        if not success:
            await ctx.send(result)
            return

        member = result

        prompt = await ctx.send(f'Click ✅ within 60 seconds to message <@{member.id}> with:\n\n{msg}')
        await prompt.add_reaction('✅')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id and str(reaction.emoji) == '✅'
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:

            try:
                await member.send(f'''{msg}\n\n{self.bot.config['bot_emoji']} *This message was delivered by the {self.bot.guild} staff.*''')
            except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
                await ctx.send(f'Could not message user. Error: {type(e).__name__}, {e}')
                return

            await ctx.send('Sent successfully!')



    # @checks.is_mod()
    # @commands.command()
    # async def fetch(self, ctx, *, arg):
    #     channel = self.bot.get_channel(698553933098123284)
    #     msg = await channel.fetch_message(713814437177589801)
    #
    #     print(channel)
    #     print(msg)
    #
    #     users = await msg.reactions[0].users().flatten()
    #
    #     role = channel.guild.get_role(715344729390448762)
    #     for u in users:
    #         if u in channel.guild.members:
    #             print(f'adding to {str(u)}')
    #             await u.add_roles(role)
    #             print(f'added to {str(u)}')
    #
    #     await ctx.message.add_reaction('✅')

    @commands.command()
    async def pet(self, ctx):
        if self.pets >= self.max_pets:
            return await ctx.send(f'''_{self.bot.user.name} is all petted out and sleeping now._ {self.bot.config['sleep_emoji']}''')
        self.pets += 1

        if self.bot.is_kooper() and random.random() < 0.05:
            await ctx.send('<:kooper:489893009228300303> 💨')
            await ctx.send('_Kooper merely farts._')
            return

        em = random.choice(self.bot.config['pet_emoji'])
        msg = f'''{em}💙'''
        await ctx.send(f'{msg} _\\*is pet\\* _ x {self.pets}')

    @checks.is_bot_admin()
    @commands.command()
    async def maxpets(self, ctx, *, arg):
        try:
            self.max_pets = int(arg)
        except ValueError:
            return await send_message(ctx, 'Type a number.', error=True)
        await ctx.message.add_reaction('✅')

    @checks.is_bot_admin()
    @commands.command()
    async def resetpets(self, ctx):
        self.pets = 0
        await ctx.send('Done.')

    @commands.command()
    async def poll(self, ctx, *, arg):
        emoji = []
        emoji = list(re.findall(emojiPattern, arg, flags=re.DOTALL)) + list(
            re.findall(customEmojiPattern, arg, flags=re.DOTALL))
        msg = await ctx.send(f"**Poll time! <@{ctx.author.id}> asks:**\n{arg}")
        for reaction in emoji:
            await msg.add_reaction(reaction.strip('<> '))

    @checks.is_bot_admin()
    @commands.command(aliases=['git', 'v', 'ver', 'stats'])
    async def about(self, ctx, *, arg=''):
        # revision = subprocess.check_output(['git', 'show', '--quiet', '--pretty=format:%H|%at|%an|%s', 'HEAD'])
        try:
            n = int(arg)
        except ValueError:
            n = 1

        revisions = subprocess.check_output(['git', 'log', '--quiet', '-n', str(n), '--pretty=format:%H|%at|%an|%s']).decode('UTF-8').split('\n')

        e = discord.Embed()
        for revision in revisions:
            hash, ts, name, commit_msg = revision.split('|')
            d = datetime.fromtimestamp(int(ts))
            now = datetime.utcnow()
            d = now - d
            e.add_field(name=f'`{hash[:6]}`', value=f'''{simplify_timedelta(d)} ago\n{commit_msg} - {name}''', inline=False)

        e.title = self.bot.user.name
        e.color = 0xa991e8
        await ctx.send(embed=e)


#
#     async def band_test(self):
#         cn = self.bot.get_channel(723013268809056286)
#         msg = ''':musical_note:  **jacob's bad gavin**
# by <@232650437617123328>  [`0:31`]
#
# _make yours on <https://goodbyevolcanohigh.com/>_'''
#         sent = await cn.send(msg, file=discord.File('data/jacobs-bad-gavin.mp3'))
#
#         for reaction in ['<:fang_sunglasses1:721410318710079490>', '<:reed_thumbsup:721410319510929449>']:
#             await sent.add_reaction(reaction.strip('<>'))




def setup(bot):
    misc = Misc(bot)
    bot.add_cog(misc)
    bot.misc = misc
