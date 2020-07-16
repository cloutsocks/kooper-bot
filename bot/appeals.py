
import discord
from discord.ext import commands

ICON_MAIL = '✉'
ICON_APPROVE = '✅'
ICON_DENY = '❌'

class Appeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot or member.guild != self.bot.appeals_guild:
            return

        try:
            ban = await self.bot.guild.fetch_ban(member)
        except Exception:
            await member.send('''You have been automatically kicked from the appeals server, as you don\'t have a removal on record for the KO_OP server. <:kooper:489893009228300303>
            
If you\'d like to join it, head over to https://discord.gg/ko-op !''')
            await member.kick()
            return

        arrow = '<:arrow:727614211932291183>'

        await self.bot.mod_cn.send(f'{arrow} {member} has just joined the Appeals Server. I wonder what they\'ll say? They were banned for: `{ban.reason}`')
        overwrites = {
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        topic = f'Appeal channel for {member}'
        cn = await member.guild.create_text_channel(str(member.id), overwrites=overwrites, topic=topic)

        msg = f'''<@{member.id}> You were removed from the KO_OP discord for: `{ban.reason}`

{arrow} You may write an appeal here and it will be delivered to us.

{arrow} We actively review appeals when they are submitted. **Unsuccessful appeals may not receive a response.**

{arrow} You **must** remain in this server for your appeal to be processed.

{arrow} We may contact you by bot to discuss things. Make **sure** DMs are enabled for this server. **Do not contact a staff member or any other user to discuss your removal or appeal: your appeal will be denied if you do so.**

{arrow} If you are removed from this server, your appeal has been processed. If you received a message welcoming you back, cool! If not, it was denied and your removal is being upheld.

{arrow} If you leave this server, you will be automatically banned and **you will no longer be able to appeal**.'''

        await cn.send(msg)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild != self.bot.appeals_guild:
            return

        try:
            ban = await self.bot.guild.fetch_ban(member)
        except Exception:
            return

        for channel in self.bot.appeals_guild.text_channels:
            if channel.name == str(member.id):
                await channel.delete()

        await self.bot.mod_cn.send(f'<:bluearrow:732168254184882209> {member} left the Appeals Server voluntarily. They were banned from it and will not be able to appeal any longer. They were banned for: `{ban.reason}`')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot \
                or message.guild != self.bot.appeals_guild \
                or message.channel.name != str(message.author.id):
            return

        try:
            ban = await self.bot.guild.fetch_ban(message.author)
        except Exception:
            return

        appeal = f'''🍎 Appeal from **{message.author}** / <@{message.author.id}>
ID: {message.author.id}
Ban Reason: `{ban.reason}`
```{message.content}```'''

        forwarded_msg = await self.bot.get_channel(728690876393717760).send(appeal)
        for reaction in [ICON_MAIL, ICON_APPROVE, ICON_DENY]:
            await forwarded_msg.add_reaction(reaction.strip('<> '))


def setup(bot):
    appeals = Appeals(bot)
    bot.add_cog(appeals)
    bot.appeals = appeals
