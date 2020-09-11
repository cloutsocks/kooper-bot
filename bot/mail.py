import discord
from discord.ext import commands

import checks

from discord import Webhook, RequestsWebhookAdapter

from common import whois_text, find_members, send_message, get_member_or_search, idPattern, DBL_BREAK, FIELD_BREAK


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
    async def mail(self, ctx, *, arg):

        category = self.bot.get_channel(self.bot.config['mail_category'])
        success, result = await get_member_or_search(self.bot, ctx.message.guild, arg)
        if not success:
            await ctx.send(result)
            return

        member = result
        channel = None
        found = False

        for cn in category.text_channels:
            try:
                uid = int(cn.topic)
            except Exception:
                continue

            if channel is None and uid == member.id:
                channel = cn
                found = True
                break

        if channel is None:
            channel = await self.bot.guild.create_text_channel(f'📨┊{str(member)}', category=category, topic=str(member.id))
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


        category = self.bot.get_channel(self.bot.config['mail_category'])

        '''
        dm from user
        '''
        if message.guild is None:
            if message.author.id not in self.user_channels_map:

                channel = None
                member = self.bot.guild.get_member(message.author.id)
                if member is None:
                    return

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
                    channel = await self.bot.guild.create_text_channel(f'📨┊{str(member)}', category=category,
                                                                       topic=str(member.id))

                self.user_channels_map[member.id] = (member, channel)
            else:
                member, channel = self.user_channels_map[message.author.id]

            webhook = await get_mail_hook(channel)

            text = message.content
            links = '\n'.join([attachment.url for attachment in message.attachments])
            if links:
                text = text + '\n' + links

            await webhook.send(text, username=member.name, avatar_url=member.avatar_url)
            # await channel.send(f'**{member}**: {message.content}')
            await message.add_reaction('✅')
            return


        '''
        outgoing from staff
        '''
        # todo check if mod

        if message.channel.category != category or '##' in message.content or message.content.startswith('.') or message.content.startswith("'"):
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
    # @checks.is_mod()
    # @commands.command()
    # async def close(self, ctx):
    #     if ctx.guild != self.bot.mail_guild:
    #         return
    #
    #     await ctx.channel.delete()


def setup(bot):
    mail = Mail(bot)
    bot.add_cog(mail)
    bot.mail = mail



# import discord
# from discord.ext import commands
#
# import checks
#
#
# class Mail(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#     @checks.is_mod()
#     @commands.command(aliases=['resolved'])
#     async def resolve(self, ctx):
#         if ctx.guild != self.bot.mail_guild:
#             return
#
#         if not ctx.channel.name.startswith('✅┊'):
#             await ctx.channel.edit(name=f'✅┊{ctx.channel.name}')
#
#     @commands.Cog.listener()
#     async def on_message(self, message):
#         if not message.author.bot or message.guild != self.bot.mail_guild:
#             return
#
#         if message.channel.name.startswith('✅┊'):
#             await message.channel.edit(name=f'{message.channel.name[2:]}')
#
#     @checks.is_mod()
#     @commands.command()
#     async def close(self, ctx):
#         if ctx.guild != self.bot.mail_guild:
#             return
#
#         await ctx.channel.delete()
#
#
# def setup(bot):
#     mail = Mail(bot)
#     bot.add_cog(mail)
#     bot.mail = mail
