import discord
from discord.ext import commands

import checks


class Mail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.is_mod()
    @commands.command(aliases=['resolved'])
    async def resolve(self, ctx):
        if ctx.guild != self.bot.mail_guild:
            return

        if not ctx.channel.name.startswith('✅┊'):
            await ctx.channel.edit(name=f'✅┊{ctx.channel.name}')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot or message.guild != self.bot.mail_guild:
            return

        if message.channel.name.startswith('✅┊'):
            await message.channel.edit(name=f'{message.channel.name[2:]}')

    @checks.is_mod()
    @commands.command()
    async def close(self, ctx):
        if ctx.guild != self.bot.mail_guild:
            return

        await ctx.channel.delete()


def setup(bot):
    mail = Mail(bot)
    bot.add_cog(mail)
    bot.mail = mail
