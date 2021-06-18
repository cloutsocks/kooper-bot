import gspread
import discord
from discord.ext import commands
from common import apply_emoji

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_text = None
        self.waiting_cn = None
        self.msg_cache = {}

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    async def on_load(self):

        try:
            self.waiting_cn = self.bot.get_channel(self.bot.config['waiting_cn'])
        except KeyError:
            pass

        gc = gspread.service_account(filename='config/service_account.json')
        spreadsheet = gc.open_by_key(self.bot.config['sheets']['data'])
        sheet = spreadsheet.worksheet('welcome_message')
        lines = sheet.col_values(1)

        self.welcome_text = []
        msg = ''

        for line in lines:
            line = apply_emoji(self.bot, line[:1990])
            if len(msg) + len(line) > 1990:
                self.welcome_text.append(msg)
                msg = ''
            else:
                msg += line + '\n'

        if msg:
            self.welcome_text.append(msg)

    async def send_message(self, member):
        for text in self.welcome_text:
            try:
                await member.send(text)
            except Exception:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.welcome_text:
            await self.bot.mod_cn.send(f'❌ **Could not load the welcome message, so none was sent to recent join!**')
            return

        if member.guild == self.bot.guild and member.id == 340838512834117632:
            await self.send_mesage(member)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        await self.reaction_action('add', payload)

    async def reaction_action(self, action, payload):

        if action != 'add':
            return

        if not self.waiting_cn:
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        if channel != self.waiting_cn:
            return

        member = self.bot.guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            message = self.msg_cache[payload.message_id]
        except KeyError:
            message = await channel.fetch_message(payload.message_id)
            self.msg_cache[payload.message_id] = message

        await message.remove_reaction(payload.emoji, member)

        emoji = str(payload.emoji)
        if emoji != '♻️':
            return

        await self.send_message(member)


def setup(bot):
    welcome = Welcome(bot)
    bot.add_cog(welcome)
    bot.welcome = welcome
