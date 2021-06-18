from discord.ext import commands
import asyncio
import sqlite3
import traceback
import discord
import inspect
import textwrap
from contextlib import redirect_stdout
import io
import sys

# to expose to the eval command
import datetime
from collections import Counter

from common import id_pattern

class Admin(commands.Cog):
    """Admin-only commands that make the bot dynamic."""

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await ctx.bot.is_owner(ctx.author)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.command()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    def reload(self, module):
        self.bot.unload_extension(module)
        self.bot.load_extension(module)

    @commands.command(name='_clear', aliases=['cl'], hidden=True)
    async def _clear(self, ctx):
        print('\n' * 200, '=== Cleared ===')

    @commands.command(name='reload', aliases=['re', 'ref'])
    async def _reload(self, ctx, *, arg):
        """Reloads a module."""

        if self.bot.config.get('disable_hot_reload', False):
            return

        match = id_pattern.search(arg)
        if match:
            uid = int(match.group(1))
            if uid != self.bot.user.id:
                return

            arg = arg.replace(match.group(0), '').strip()

        if ctx.invoked_with == 'ref':
            self.bot.wfm = {}
            self.bot.wfr = {}

        try:
            self.reload(arg)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send(f'✅ Reloaded {arg}')

    @commands.command(name='reloadall', aliases=['ra'])
    async def _reload_all(self, ctx, *, arg=''):
        """Reloads all modules."""

        if self.bot.config.get('disable_hot_reload', False):
            return

        match = id_pattern.search(arg)
        if match:
            uid = int(match.group(1))
            if uid != self.bot.user.id:
                return

        self.bot.wfm = {}
        self.bot.wfr = {}

        try:
            for extension in self.bot.exts:
                self.bot.unload_extension(extension)
                self.bot.load_extension(extension)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('✅')

    @commands.command(name='restart')
    async def _restart(self, ctx, arg=''):
        match = id_pattern.search(arg)
        if not match:
            return

        uid = int(match.group(1))
        if uid != self.bot.user.id:
            return

        await ctx.send('Force restarting the bot, this should not be done often or repeatedly or you risk being blacklisted by Discord.')
        self.execute_restart(by_command=True)

    def execute_restart(self, by_command):
        print('[SYS] Restarting by command' if by_command else '[SYS] Restarting')
        sys.exit(1)

def setup(bot):
    admin = Admin(bot)
    bot.add_cog(admin)
