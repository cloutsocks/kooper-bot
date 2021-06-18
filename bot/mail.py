import discord
from discord.ext import commands

import checks

from discord import Webhook, RequestsWebhookAdapter

from common import whois_text, find_members, send_message, get_member_or_search, id_pattern, DBL_BREAK, FIELD_BREAK

APPROVE_EMOJI = '🆗'

# db = SqliteDatabase('mail.db')
#
# class BaseModel(Model):
#     class Meta:
#         database = db
#
# class Mail(BaseModel):
#     user_id = IntegerField()
#     log = CharField()

async def get_mail_hook(channel):
    try:
        webhooks = await channel.webhooks()
        webhook = webhooks[0]
    except Exception:
        webhook = await channel.create_webhook(name='Mail Webhook', reason=None)
    return webhook

class Mail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_channels_map = {}

    # @checks.is_mod()
    # @commands.command()
    # async def wh(self, ctx, *, arg):
    #     try:
    #         webhooks = await ctx.channel.webhooks()
    #         webhook = webhooks[0]
    #     except Exception:
    #         webhook = await ctx.channel.create_webhook(name='Mail Webhook', reason=None)
    #
    #     await webhook.send(arg, username=ctx.author.name, avatar_url=ctx.author.avatar_url)

    @checks.is_mod()
    @commands.command()
    async def close(self, ctx):
        mail_category = self.bot.get_channel(self.bot.config['mail_category'])
        if ctx.channel.category != mail_category:
            return

        try:
            uid = int(ctx.channel.topic)
        except Exception:
            return

        if uid in self.user_channels_map:
            del self.user_channels_map[uid]

        await ctx.channel.delete()

    @checks.is_mod()
    @commands.command()
    async def mail(self, ctx, *, arg):

        mail_category = self.bot.get_channel(self.bot.config['mail_category'])
        success, result = await get_member_or_search(self.bot, ctx.message.guild, arg)
        if not success:
            await ctx.send(result)
            return

        member = result
        channel = None
        found = False

        for cn in mail_category.text_channels:
            try:
                uid = int(cn.topic)
            except Exception:
                continue

            if channel is None and uid == member.id:
                channel = cn
                found = True
                break

        if channel is None or self.bot.get_channel(channel.id) is None:
            overwrites = {
                self.bot.guild.default_role: discord.PermissionOverwrite(read_messages=False)
            }
            channel = await self.bot.guild.create_text_channel(f'📨┊{str(member)}', category=mail_category, topic=str(member.id))
            await channel.send(f'''## _Any messages sent here will be delivered to {member.mention} **unless** they start with a `.` or contain `##`. Message edits are **not** yet supported. If you do not get a ✅ reaction, your message was not delivered._
-----''')

        self.user_channels_map[member.id] = (member, channel)

        if found:
            await ctx.send(f'Found existing channel {channel.mention}')
        else:
            await ctx.send(f'Created {channel.mention}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        member_role = None
        if 'applications_category' in self.bot.config and 'member_role_id' in self.bot.config:
            applications_category = self.bot.get_channel(self.bot.config['applications_category'])
            member_role = self.bot.guild.get_role(self.bot.config['member_role_id'])

        is_application = False
        category = mail_category = self.bot.get_channel(self.bot.config['mail_category'])
        emoji = '📨'

        overwrites = {
            self.bot.guild.default_role: discord.PermissionOverwrite(read_messages=False)
        }
        is_application
        '''
        dm from user
        '''
        if message.guild is None:
            if message.author.id not in self.user_channels_map:

                channel = None
                member = self.bot.guild.get_member(message.author.id)
                if member is None:
                    return

                if member_role is not None and member_role not in member.roles:
                    is_application = True
                    category = applications_category
                    emoji = '🌱'

                for cn in category.text_channels:
                    try:
                        uid = int(cn.topic)
                    except Exception:
                        continue

                    if uid == message.author.id:
                        channel = cn
                        found = True
                        break

                if channel is None:
                    channel = await self.bot.guild.create_text_channel(f'{emoji}┊{str(member)}', category=category,
                                                                       topic=str(member.id))
                    if is_application:
                        if hasattr(member, 'nick') and member.nick:
                            member_string = f'**{member}** aka **{member.nick}** / <@{member.id}> ({member.id})'
                        else:
                            member_string = f'**{member}** / <@{member.id}> ({member.id})'

                        await channel.send(f'''🌱 New application from {member_string}\nReact with a {APPROVE_EMOJI} to any message from them to approve them as members (equivalent to, they receive the `Member` role).''')

                self.user_channels_map[member.id] = (member, channel)
            else:
                member, channel = self.user_channels_map[message.author.id]
                if self.bot.get_channel(channel.id) is None:
                    if member_role is not None and member_role not in member.roles:
                        is_application = True
                        category = applications_category
                        emoji = '🌱'

                    channel = await self.bot.guild.create_text_channel(f'{emoji}┊{str(member)}', category=category, topic=str(member.id))
                    self.user_channels_map[member.id] = (member, channel)

            webhook = await get_mail_hook(channel)

            text = message.content
            links = '\n'.join([attachment.url for attachment in message.attachments])
            if links:
                text = text + '\n' + links

            replicated_message = await webhook.send(text, username=member.name, avatar_url=member.avatar_url, wait=True)
            if is_application:
                await replicated_message.add_reaction(APPROVE_EMOJI)

            # await channel.send(f'**{member}**: {message.content}')
            await message.add_reaction('✅')
            return


        '''
        outgoing from staff
        '''
        # todo check if mod

        if message.channel.category != mail_category or '##' in message.content or message.content.startswith('.') or message.content.startswith("'"):
            return

        try:
            uid = int(message.channel.topic)
        except Exception:
            return

        if uid not in self.user_channels_map:
            member = self.bot.guild.get_member(uid)
            if member is None:
                await message.channel.send(f'## ❌ Error: could not find member <@{uid}>')
                return

            channel = message.channel
            self.user_channels_map[member.id] = (member, channel)
        else:
            member, channel = self.user_channels_map[uid]
            if self.bot.get_channel(channel.id) is None:
                channel = await self.bot.guild.create_text_channel(f'📨┊{str(member)}', category=mail_category, topic=str(member.id))
                self.user_channels_map[member.id] = (member, channel)

        text = message.content
        links = '\n'.join([attachment.url for attachment in message.attachments])
        if links:
            text = text + '\n' + links

        try:
            await member.send(text)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            await message.channel.send(f'## ❌ Could not message user. Error: {type(e).__name__}, {e}')
            return

        await message.add_reaction('✅')

        # channel = discord.utils.get(guild.channels, name=Channel_Name)

    # @checks.is_mod()
    # @commands.command(aliases=['resolved'])
    # async def resolve(self, ctx):
    #     if ctx.guild != self.bot.mail_guild:
    #         return
    #
    #     if not ctx.channel.name.startswith('✅┊'):
    #         await ctx.channel.edit(name=f'✉️┊{ctx.channel.name}')
    #
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if not message.author.bot or message.guild != self.bot.mail_guild:
    #         return
    #
    #     if message.channel.name.startswith('✅┊'):
    #         await message.channel.edit(name=f'{message.channel.name[2:]}')
    #

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_action('add', payload)

    async def reaction_action(self, action, payload):
        if payload.user_id == self.bot.user.id:
            return

        emoji = str(payload.emoji)
        if emoji != APPROVE_EMOJI:
            return

        approver = self.bot.guild.get_member(payload.user_id)
        if approver is None:
            return

        if not approver.guild_permissions.manage_guild:
            return

        try:
            applications_category = self.bot.get_channel(self.bot.config['applications_category'])
            member_role = self.bot.guild.get_role(self.bot.config['member_role_id'])
        except KeyError:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel.category != applications_category:
            return

        try:
            uid = int(channel.topic)
        except Exception:
            await channel.send(f'## ❌ Could not parse user id from channel topic.')
            return

        applicant = self.bot.guild.get_member(uid)
        if applicant is None:
            await channel.send(f'## ❌ Could not locate <@{uid}>')
            return

        if member_role in applicant.roles:
            await channel.send(f'## ❌ User already approved.')
            return

        if hasattr(applicant, 'nick') and applicant.nick:
            applicant_string = f'**{applicant}** aka **{applicant.nick}** / <@{applicant.id}> ({applicant.id})'
        else:
            applicant_string = f'**{applicant}** / <@{applicant.id}> ({applicant.id})'

        try:
            await applicant.add_roles(member_role)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
            await channel.send(f'## ❌ Could not add role to {applicant_string}. Error: {type(e).__name__}, {e}')
            return

        if uid in self.user_channels_map:
            del self.user_channels_map[uid]

        log_msg = f'🌱 {applicant_string} was __approved__ by {approver}'
        await channel.send(f'## {log_msg}\nThey were sent a welcome message by Naomi.)')

        if 'applications_log_cn' in self.bot.config:
            log_cn = self.bot.get_channel(self.bot.config['applications_log_cn'])
            await log_cn.send(log_msg)


def setup(bot):
    mail = Mail(bot)
    bot.add_cog(mail)
    bot.mail = mail