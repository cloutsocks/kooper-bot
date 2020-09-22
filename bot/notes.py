import discord
import checks
import random

import time
import pytz

from discord.ext import commands
from common import whois_text, find_members, send_message, get_member_or_search, idPattern, DBL_BREAK, FIELD_BREAK, simplify_timedelta

from peewee import *
from datetime import datetime

ICON_NOTE = '📝'

db = SqliteDatabase('notes.db')

class BaseModel(Model):
    class Meta:
        database = db


class Note(BaseModel):
    for_id = IntegerField()
    for_handle = CharField(null=True)
    by_id = IntegerField(null=True)
    by_handle = CharField(null=True)
    guild_id = IntegerField(null=True)
    t = IntegerField()
    text = CharField()


def create_tables():
    with db:
        db.create_tables([Note])


class Notes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.paused = False

        if self.bot.is_ready():
            self.bot.loop.create_task(self.on_load())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.on_load()

    async def on_load(self):
        pass

    @checks.is_mod()
    @commands.command(aliases=['note'])
    async def notes(self, ctx, *, arg=''):
        if self.paused:
            await ctx.send('Notes currently paused.')
            return

        found = await find_members(self.bot, ctx.message.guild, arg)
        whois = whois_text(self.bot, found, show_extra=True, try_embed=True)
        if not isinstance(whois, tuple):
            await ctx.send(whois)
            return

        _, e = whois
        user, = found

        query = Note.select().where(Note.for_id == user.id)
        notes = [note for note in query]

        if not notes:
            await ctx.send(f'No notes on file for {user.mention} / {user}', embed=e)
            return

        parts = []
        for note in notes:
            when = simplify_timedelta(datetime.now() - datetime.fromtimestamp(note.t)).replace('*', '')
            part = f'''{ICON_NOTE} {note.text}
_by **{note.by_handle.split('#')[0]}**, `{when} ago`_'''
            parts.append(part)

        await ctx.send(f'{len(notes)} notes for {user.mention} / {user}', embed=e)
        await ctx.send('\u200b\n' + DBL_BREAK.join(parts))
        # await ctx.send(f'{DBL_BREAK}'.join(parts))

    @checks.is_mod()
    @commands.command(name='addnote', aliases=['noteadd'])
    async def add_note_command(self, ctx, *, arg=''):
        try:
            query, text = arg.split(' ', 1)
        except ValueError:
            await send_message(ctx, 'Please include a message to send with. Usage: `.msg <member query> <msg>',
                               error=True)
            return

        success, result = await get_member_or_search(self.bot, ctx.guild, query)
        if not success:
            await ctx.send(result)
            return

        user = result
        self.add_note(user, ctx.author, ctx.guild, text)
        await ctx.send(f'{ICON_NOTE} note added for {user.mention} / {user}')

    def add_note(self, user, by, guild, text):
        guild_id = guild.id if guild is not None else None
        note_row = Note(for_id=user.id,
                        for_handle=str(user),
                        by_id=by.id,
                        by_handle=str(by),
                        guild_id=guild_id,
                        t=int(time.time()),
                        text=text)
        note_row.save()

    @checks.is_jacob()
    @commands.command(name='pausenotes', aliases=['pausenote', 'notepause', 'notespause'])
    async def pause_notes(self, ctx):
        self.paused = not self.paused
        await ctx.send(f'`paused = {self.paused}`')

    @checks.is_jacob()
    @commands.command()
    async def make_notes_db(self, ctx):
        create_tables()


def setup(bot):
    notes = Notes(bot)
    bot.add_cog(notes)
    bot.notes = notes
