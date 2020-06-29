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
from one_shots.wg_misc import add_role_to_everyone

initial_extensions = (
    'common',
    'error',
    'config',
    'misc',
    'mod'
    # 'mystery',
)


def command_prefixes(bot, message):
    return ['.', ';', ',']


# invite https://discordapp.com/api/oauth2/authorize?client_id=679161047000809473&permissions=2146827601&scope=bot



# kooper invite https://discordapp.com/api/oauth2/authorize?client_id=715609234561302571&permissions=2146827601&scope=bot

# naomi invite https://discordapp.com/api/oauth2/authorize?client_id=720740582288261150&permissions=2146827601&scope=bot
# rosa invite https://discordapp.com/api/oauth2/authorize?client_id=720741045008072704&permissions=2146827601&scope=bot


class ToxelBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=command_prefixes)

        # self.help_command = None

        self.config = None
        self.misc = None
        self.mod = None

        self.wfr = {}
        self.wfm = {}

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()

    def clear_wait_fors(self, uid):
        self.wfr.pop(uid, None)
        self.wfm.pop(uid, None)


bot = ToxelBot()

# @bot.check
# async def debug_restrict_jacob(ctx):
#     return ctx.message.author.id == 232650437617123328 or ctx.message.author.id == 340838512834117632


@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    status = bot.config['playing']
    playing = discord.Game(name=status)
    await bot.change_presence(activity=playing)

    bot.slur_log_cn = bot.get_channel(720817629954179073)

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



async def handle(guild, member):
    print(member.name)
    await member.send("You have been banned as you are suspected to be a raider. If this was a mistake, reach out to one of us in the coming days.")
    await member.ban(reason="Suspected raider (Automatic)")


async def ohdear():
    futs = []
    guild = bot.get_guild(372482304867827712)
    for member in guild.members:
        if member.joined_at < datetime.datetime.now() - datetime.timedelta(minutes=10):
            continue

        futs.append(handle(guild, member))

    print(await asyncio.gather(*futs, return_exceptions=True))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    uid = message.author.id
    if message.guild is None and uid not in bot.config['creator_ids']:
        return

    await bot.mod.abuse_check(message)

    await bot.process_commands(message)
    if uid in bot.wfm:
        waiter = bot.wfm[uid]
        if waiter['channel'] != message.channel:
            return
        try:
            if time.time() > waiter['expires']:
                del bot.wfm[uid]
                return
        except KeyError:
            pass

        await waiter['handler'].handle_message(message)


@bot.event
async def on_member_join(member):
    await bot.mod.join_check(member)


@bot.command(name='reloadall', aliases=['reall', 'ra'])
@checks.is_jacob()
async def _reloadall(ctx, arg=None):
    """Reloads all modules."""

    # if bot.config.get('disable_hot_reload', True):
    #     return

    bot.wfm = {}
    bot.wfr = {}
    try:
        for extension in initial_extensions:
            bot.unload_extension(extension)
            bot.load_extension(extension)
    except Exception as e:
        await ctx.send(f'```py\n{traceback.format_exc()}\n```')
    else:
        await ctx.send('✅')


print('Starting')
bot.run(bot.config['token'])
