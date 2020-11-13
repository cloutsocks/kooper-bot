import asyncio
import re

import discord
import random

from datetime import datetime, timedelta

import discord
from discord.ext import commands
from common import whois_text, find_members, send_message, get_member_or_search, idPattern, DBL_BREAK, FIELD_BREAK

import checks

filter_remove = re.compile(
    r'discord\.gg/(?!ko-op\b)|retard|loli|shota|nibb(?:a|er)|nigg|\bfag|porn|\bnazi|hentai|yaoi|tranny|tranni|\brape|sneed|\brapin|\brapist|slave|\bcunt\b|41%|yiff|milf|r34|rule\s?34|\bree+\b')

filter_warn = re.compile(
    'trigger(ed|ing)|nudes|kotaku|pedophile|transgenderism|\bcp\b|pedo\b|4chan|2ch|all\slives\smatter|suicide|waifu')


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    async def on_load(self):
        if 'mod_cn' in self.bot.config:
            self.bot.mod_cn = self.bot.get_channel(self.bot.config['mod_cn'])

        if 'log_cn' in self.bot.config:
            self.bot.log_cn = self.bot.get_channel(self.bot.config['log_cn'])

        if self.bot.is_kooper():
            self.bot.slur_log_cn = self.bot.get_channel(720817629954179073)
            self.bot.trotter_cn = self.bot.get_channel(727625945288016134)

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.is_kooper() and self.bot.guild is not None and message.guild == self.bot.guild:
            await self.abuse_check(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild == self.bot.guild:
            await self.join_check(member)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.bot.mod_cn.send(f'📥 **Invite {self.bot.guild} created by {invite.inviter} / <@{invite.inviter.id}>**')

    async def join_check(self, m):
        if m.joined_at and m.created_at:
            now = datetime.utcnow()
            joined_ago = now - m.joined_at
            created_ago = now - m.created_at

            if m.joined_at - m.created_at < timedelta(minutes=15):
                await self.bot.mod_cn.send(f'🕑 **User joined within 15 minutes of making an account:**\n{m} / <@{m.id}>')

    @checks.is_mod()
    @commands.command()
    async def whois(self, ctx, *, arg):
        found = await find_members(self.bot, ctx.message.guild, arg)
        whois = whois_text(self.bot, found, show_extra=True, try_embed=True)
        if isinstance(whois, tuple):
            text, e = whois
            await ctx.send(text, embed=e)
        else:
            await ctx.send(whois)

    @checks.is_mod()
    @commands.command()
    async def kick(self, ctx, *, arg):
        try:
            query, msg = arg.split(' ', 1)
        except ValueError:
            await send_message(ctx, 'Please include a message to send with the kick. Usage: `.kick <member query> <msg>', error=True)
            return

        success, result = await get_member_or_search(self.bot, ctx.message.guild, query)
        if not success:
            await ctx.send(result)
            return

        member = result
        if hasattr(member, 'nick') and member.nick:
            member_string = f'**{member}** aka **{member.nick}** / <@{member.id}> ({member.id})'
        else:
            member_string = f'**{member}** / <@{member.id}> ({member.id})'

        prompt = await ctx.send(f'Click ✅ within 60 seconds to kick {member_string} with the message:\n\n{msg}\n\n_They will be notified they can rejoin at any time after acknolwedging it._')
        await prompt.add_reaction('✅')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id and str(reaction.emoji) == '✅'
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return

        try:
            await member.send(f'You have been kicked for: `{msg}`\n\nYou may rejoin at any time after acknolwedging or resolving the issue.')
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            await ctx.send(f'Could not message {member_string}. Error: {type(e).__name__}, {e}')
        else:
            await ctx.send('Message sent successfully!')

        try:
            await member.kick()
        except AttributeError:
            await ctx.send(f'{member_string} is not on the server, so they were not kicked.')
            return
        except (discord.Forbidden, discord.HTTPException) as e:
            await ctx.send(f'Could not kick {member_string}. Error: {type(e).__name__}, {e}')

        log_msg = await ctx.send(f'👟 {member_string} was __kicked__.')
        await self.bot.log_cn.send(f'👟\n {member_string} was __kicked__ by {ctx.author} for: `{msg}`\n\n Context: {log_msg.jump_url}')
        try:
            self.bot.notes.add_note(member, self.bot.user, ctx.guild, f'`.kick`ed by {ctx.author} for: `{msg}`')
        except Exception:
            pass

    @checks.is_mod()
    @commands.command()
    async def ban(self, ctx, *, arg):
        try:
            query, msg = arg.split(' ', 1)
        except ValueError:
            await send_message(ctx, 'Please include a message to send with the ban. Usage: `.ban <member query> <msg>', error=True)
            return

        success, result = await get_member_or_search(self.bot, ctx.message.guild, query, use_hackban=True)
        if not success:
            await ctx.send(result)
            return

        member = result
        prompt = await ctx.send(f'React to this message within 60 seconds with the number of days of messages to delete and I will ban <@{member.id}> with the message:\n\n{msg}\n\n_They will not be able to rejoin unless they are unbanned._')
        nums = ['0️⃣', '1️⃣', '2️⃣']
        for num in nums:
            await prompt.add_reaction(num)

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id and str(reaction.emoji) in nums
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return

        days = nums.index(str(reaction.emoji))

        was_banned = False
        try:
            await ctx.guild.unban(discord.Object(id=member.id))
            was_banned = True
        except Exception as e:
            pass

        verb = '_rebanned_' if was_banned else 'banned'

        if isinstance(member, discord.Object):
            member_string = f'<@{member.id}> / {member.id}'
            u = None
            try:
                u = await self.bot.fetch_user(member.id)
                member_string = f'**{u}** / <@{u.id}> ({u.id})'
            except (discord.NotFound, discord.HTTPException) as e:
                pass

            try:
                await ctx.guild.ban(member, reason=msg, delete_message_days=days)
            except Exception as e:
                await ctx.send(f'Could not ban {member_string} Error: {type(e).__name__}, {e}')
            else:
                log_msg = await ctx.send(f'🔨 [Off-server] {member_string} was **{verb}** and all of their messages sent within the past {days} days were deleted. They were not notified, as they are not on the server.')
                await self.bot.log_cn.send(
                    f'🔨\n [Off-server] {member_string} was **{verb}** by {ctx.author} for: `{msg}`\n\nAll of their messages sent within the past {days} days were deleted. They were not notified, as they are not on the server. Context: {log_msg.jump_url}')
                try:
                    if u:
                        self.bot.notes.add_note(u, self.bot.user, ctx.guild, f'`.ban`ned by {ctx.author} for: `{msg}`')
                except Exception:
                    pass
            return

        if hasattr(member, 'nick') and member.nick:
            member_string = f'**{member}** aka **{member.nick}** / <@{member.id}> ({member.id})'
        else:
            member_string = f'**{member}** / <@{member.id}> ({member.id})'

        try:
            await member.send(f'You have been banned for: `{msg}`')
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            await ctx.send(f'Could not message {member_string}. Error: {type(e).__name__}, {e}')
        else:
            await ctx.send('Ban message sent successfully!')

        try:
            await member.ban(reason=msg, delete_message_days=days)
        except Exception as e:
            await ctx.send(f'Could not ban {member_string} Error: {type(e).__name__}, {e}')
        else:
            log_msg = await ctx.send(f'🔨 {member_string} was **{verb}** and all of their messages sent within the past {days} days were deleted.')
            await self.bot.log_cn.send(f'🔨\n {member_string} was **{verb}** by {ctx.author} for: `{msg}`\n\nAll of their messages sent within the past {days} days were deleted. Context: {log_msg.jump_url}')
            try:
                self.bot.notes.add_note(member, self.bot.user, ctx.guild, f'`.ban`ned by {ctx.author} for: `{msg}`')
            except Exception:
                pass

    @checks.is_mod()
    @commands.command()
    async def unban(self, ctx, *, arg):

        match = idPattern.search(arg)
        if match:
            uid = int(match.group(1))
        else:
            try:
                uid = int(arg)
            except ValueError:
                await send_message(ctx, 'You have to include the user id or ping them: `.unban <user id or @user>', error=True)
                return

        member_string = f'<@{uid}> / {uid}'
        u = None
        try:
            u = await self.bot.fetch_user(uid)
            member_string = f'**{u}** / <@{u.id}> ({u.id})'
        except (discord.NotFound, discord.HTTPException) as e:
            pass

        try:
            await ctx.guild.unban(discord.Object(id=uid))
        except Exception as e:
            await ctx.send(f'Could not unban {member_string} Error: {type(e).__name__}, {e}')
        else:
            log_msg = await ctx.send(f'🌈 {member_string} was **unbanned**, but they have not been notified of this.')
            await self.bot.log_cn.send(f'🌈\n {member_string} was **unbanned** by {ctx.author}, but they have not been notified of this. Context: {log_msg.jump_url}')
            try:
                if u:
                    self.bot.notes.add_note(u, self.bot.user, ctx.guild, f'`.unban`ned by {ctx.author}')
            except Exception:
                pass

    @checks.is_jacob()
    @commands.command()
    async def massban(self, ctx, *, arg=''):

        m = re.search(r'\[(.*)\]', arg, flags=re.DOTALL)
        if not m:
            return await ctx.send('Include a list of ids between brackets []')

        id_text = m.group(1)
        arg = arg.replace(m.group(0), '')

        reason = arg.strip()
        if not reason:
            return await ctx.send('You have to include a reason.')

        ids = re.split(r'[\s,]+', id_text)
        uids = []
        errors = []
        for id in ids:
            try:
                id = int(id)
                uids.append(id)
            except ValueError:
                return await ctx.send(f'Invalid id {id}')
                pass

        user_text = ' '.join(f'<@{uid}>' for uid in uids)
        prompt = await ctx.send(f'This will ban: {user_text}\nwith the reason:\n```{reason}```**Note:** they will be able to see this reason if they ever appeal. Click the ✅ to confirm.')
        await prompt.add_reaction('✅')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == prompt.id and str(reaction.emoji) == '✅'

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('You took too long')
        else:
            await ctx.send('Attempting to ban...')
            for i, uid in enumerate(uids):
                try:
                    await ctx.guild.ban(discord.Object(id=uid), reason=reason)
                    await ctx.send(f'🔨 Banned <@{uid}> / {uid} [{i+1} / {len(uids)}]')
                except Exception as e:
                    await ctx.send(f'Could not ban <@{uid}> / {uid} Error: {type(e).__name__}, {e}')
            await ctx.send('😇 Done.')

    @checks.is_jacob()
    @commands.command(aliases=['servers'])
    async def guilds(self, ctx):
        guilds = '\n'.join([f'{guild.id} {guild}{" <- [here]" if guild == ctx.guild else ""}' for guild in self.bot.guilds])
        await ctx.send(f'```{guilds}```')

    @checks.is_jacob()
    @commands.command()
    async def modules(self, ctx):
        await ctx.send(f'```{self.bot.extensions.keys()}```')

    async def sync_bans(self):
        wf_guild_id = 649042459195867136
        wg_guild_id = 546468613805309962
        wf_guild = self.bot.get_guild(wf_guild_id)
        wg_guild = self.bot.get_guild(wg_guild_id)

        for entry in await wf_guild.bans():
            try:
                await wg_guild.ban(discord.Object(id=entry.user.id), reason=f'[Forwarded Ban] {entry.reason}')
                print(f'{entry.user} banned for [Forwarded Ban] {entry.reason}')
            except Exception as e:
                print(f'Could not ban <@{entry.user.id}> Error: {type(e).__name__}, {e}')

    async def abuse_check(self, message):
        if message.author.bot or message.author.guild_permissions.manage_guild:
            return

        if hasattr(message.author, 'nick') and message.author.nick:
            member_string = f'**{message.author}** aka **{message.author.nick}** / <@{message.author.id}> ({message.author.id})'
        else:
            member_string = f'**{message.author}** / <@{message.author.id}> ({message.author.id})'

        log_msg = None
        bot = self.bot
        if (match := filter_remove.search(message.content)) is not None:
            await message.delete()
            log_msg = await bot.slur_log_cn.send(
                f'{FIELD_BREAK}\n🛑 Logged `{match.group(0)}` and **auto-deleted** message from {message.author} / <@{message.author.id}> in <#{message.channel.id}>\n<{message.jump_url}>:\n\n```{message.content[:1700]}```React to ban with a message and delete # days of messages, or 👟 kick.')

        elif (match := filter_warn.search(message.content)) is not None:
            log_msg = await bot.slur_log_cn.send(
                f'{FIELD_BREAK}\n⚠ Logged `{match.group(0)}` (without deleting) from {message.author} / <@{message.author.id}> in <#{message.channel.id}>\n<{message.jump_url}>:\n\n```{message.content[:1700]}```React to ban with a message and delete # days of messages, or 👟 kick.')

        if log_msg is None:
            return

        nums = ['0️⃣', '1️⃣', '2️⃣']
        for reaction in ['👟'] + nums:
            await log_msg.add_reaction(reaction)

        def check(reaction, user):
            return reaction.message.id == log_msg.id and str(reaction.emoji) in ['👟'] + nums and user.guild_permissions.manage_guild and not user.bot

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=None, check=check)
        except asyncio.TimeoutError:
            return

        if str(reaction.emoji) == '👟':
            try:
                await message.author.send(
                    f'You have been kicked from the {self.bot.guild} Discord for your message: {message.content}\n\nYou may rejoin at any time after acknolwedging or resolving the issue.')
            except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
                await bot.slur_log_cn.send(f'Could not message {member_string}. Error: {type(e).__name__}, {e}')
            else:
                await bot.slur_log_cn.send('Message sent successfully!')

            try:
                await message.author.kick()
            except (discord.Forbidden, discord.HTTPException) as e:
                await bot.slur_log_cn.send(f'Could not kick {member_string}. Error: {type(e).__name__}, {e}')
            else:
                await bot.slur_log_cn.send(f'👟 {member_string} was _kicked_ and told why. They can rejoin at any time.')
                await bot.log_cn.send(f'👟\n {member_string} was _kicked_ via <#{bot.slur_log_cn.id}> and told why. They can rejoin at any time. Context: {log_msg.jump_url}')
                try:
                    bot.notes.add_note(message.author, bot.user, message.guild, f'Kicked via <#{bot.slur_log_cn.id}>')
                except Exception:
                    pass
            return


        try:
            days = nums.index(str(reaction.emoji))
        except IndexError:
            return

        try:
            await message.author.send(f'You were removed automatically from the {self.bot.guild} Discord for one of your messages: {message.content}')
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            await bot.slur_log_cn.send(f'Could not message {member_string}. Error: {type(e).__name__}, {e}')
        else:
            await bot.slur_log_cn.send('Ban message sent successfully!')

        try:
            await message.author.ban(reason=f'Removed for message: {message.content}', delete_message_days=days)
        except Exception as e:
            await bot.slur_log_cn.send(f'Could not ban {member_string} Error: {type(e).__name__}, {e}')
        else:
            await bot.slur_log_cn.send(
                f'🔨 {member_string} was _banned_ and all of their messages sent within the past {days} days were deleted. They were told why.')
            await bot.log_cn.send(
                f'🔨\n {member_string} was _banned_ via <#{bot.slur_log_cn.id}> and all of their messages sent within the past {days} days were deleted. They were told why. Context: {log_msg.jump_url}')
            try:
                bot.notes.add_note(message.author, bot.user, message.guild, f'Banned via <#{bot.slur_log_cn.id}>')
            except Exception:
                pass

def setup(bot):
    mod = Mod(bot)
    bot.add_cog(mod)
    bot.mod = mod
