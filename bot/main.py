import json
import os
import sys
import time
import traceback
import datetime
import asyncio
import re

import discord
from discord.ext import commands

import checks

# from one_shots.tally_meltans import tally, raffle, get_test_raid_members
# from one_shots.wg_misc import add_role_to_everyone
# from one_shots.koop_misc import add_admin_holding_server
# from one_shots.misc import tally_reactions

def command_prefixes(bot, message):
    return bot.config['prefix']


# invite https://discordapp.com/api/oauth2/authorize?client_id=ID&permissions=0&scope=bot
# invite https://discordapp.com/api/oauth2/authorize?client_id=ID&permissions=2146827601&scope=bot

class KooperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=command_prefixes)

        # self.help_command = None

        self.guild = None
        self.config = None
        self.misc = None
        self.mod = None
        self.actor = None
        self.appeals_guild = None
        self.mail_guild = None

        self.wfr = {}
        self.wfm = {}

        self.exts = [
            'common',
            'error',
            'config',
            'misc',
            'mod',
            'students'
        ]

        for extension in self.exts:
            self.load(extension)

    def clear_wait_fors(self, uid):
        self.wfr.pop(uid, None)
        self.wfm.pop(uid, None)

    def load(self, extension):
        try:
            self.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()
            
    def is_kooper(self):
        return self.guild is not None and self.guild.id == 372482304867827712


bot = KooperBot()

# @bot.check
# async def debug_restrict_jacob(ctx):
#     return ctx.message.author.id == 232650437617123328 or ctx.message.author.id == 340838512834117632

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # todo move to config?
    bot.guild = bot.get_guild(bot.config['guild'])
    print(f'is_kooper: {bot.is_kooper()}')

    status = bot.config['playing']
    playing = discord.Game(name=status)
    await bot.change_presence(activity=playing)


    try:
        bot.appeals_guild = bot.get_guild(bot.config['appeals_guild'])
    except Exception:
        pass

    if bot.appeals_guild:
        print('Loading appeals cog')
        bot.exts.append('appeals')
        bot.load('appeals')

    # try:
    #     bot.mail_guild = bot.get_guild(bot.config['mail_guild'])
    # except Exception:
    #     pass
    #
    # if bot.mail_guild:
    #     print('Loading mail cog')
    #     bot.exts.append('mail')
    #     bot.load('mail')

    try:
        bot.exts += bot.config['exts']
        for ext in bot.config['exts']:
            bot.load(ext)
    except Exception:
        pass

    print(bot.exts)

    # await replace_underscores(bot)
    # await bot.mod.sync_bans()
    # await bot.misc.add_roles_to_every_poster(680310582083452932, 680302613970944031)
    # await tally(bot, 680310582083452932)
    # await raffle(bot)
    # await get_test_raid_members(bot)
    # await raffle
    # await add_role_to_everyone(bot)
    # await bot.misc.band_test()
    # print('Done')
    # await ohdear()
    # await make_holding_server(bot)
    # await add_admin_holding_server(bot)
    # await tally_reactions(bot, '🦆', 679078888575467530, 200)



async def handle(guild, member):
    print(member.name)
    await member.send("You have been banned as you are suspected to be a raider. If this was a mistake, reach out to one of us in the coming days.")
    await member.ban(reason="Suspected raider (Automatic)")


# async def ohdear():
#     futures = []
#     guild = bot.get_guild(372482304867827712)
#     for member in guild.members:
#         if member.joined_at < datetime.datetime.now() - datetime.timedelta(minutes=10):
#             continue
#
#         futures.append(handle(guild, member))
#
#     print(await asyncio.gather(*futures, return_exceptions=True))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = message.author.id
    if message.guild is None and uid not in bot.config['creator_ids']:
        return

    if not bot.appeals_guild or message.guild and message.guild != bot.appeals_guild:
        await bot.process_commands(message)
        if uid in bot.wfm:
            waiter = bot.wfm[uid]
            if 'channel' in waiter and waiter['channel'] != message.channel:
                return
            try:
                if time.time() > waiter['expires']:
                    del bot.wfm[uid]
                    return
            except KeyError:
                pass

            await waiter['handler'].handle_message(message)



@bot.command(name='reloadall', aliases=['reall', 'ra', 'rk'])
@checks.is_jacob()
async def _reloadall(ctx):
    """Reloads all modules."""

    # if bot.config.get('disable_hot_reload', True):
    #     return

    bot.wfm = {}
    bot.wfr = {}

    try:
        for extension in bot.exts:
            bot.unload_extension(extension)
            bot.load_extension(extension)
    except Exception as e:
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        await ctx.send('✅')


print('Starting')
bot.run(bot.config['token'])
