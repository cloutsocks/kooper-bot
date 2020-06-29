import time
from collections import namedtuple

import aiohttp
import discord
import pprint

import checks

from discord.ext import commands

from common import send_message, resolve_mention, send_user_not_found, idPattern, EMOJI, DBL_BREAK

CardRecord = namedtuple('CardRecord',
                        'discord_id, discord_name, fc, ign, switch_name, title_1, title_2, pkmn_icon, color, img, quote')

ENDPOINT = 'https://wooloo.farm'


async def get_user_by_credential(realm, identifier, endpoint=ENDPOINT):
    async with aiohttp.ClientSession() as session:
        r = await session.get(ENDPOINT + '/trainer-by-credential.json',
                              params={'realm': realm, 'identifier': identifier})
        if r.status not in (200, 404):
            r.raise_for_status()
        return await r.json()


async def has_wf_ban(uid, endpoint):
    async with aiohttp.ClientSession() as session:
        r = await session.get((endpoint),
                              params={'id': uid})
        if r.status not in (204, 404):
            r.raise_for_status()

        return r.status == 204


def has_raid_info(profile):
    if not profile:
        return False, 'WF_NO_ACCOUNT'

    for key in ['friend_code', 'switch_name', 'games']:
        if key not in profile or not profile[key]:
            return False, f'WF_NOT_SET: {key}'

    sw = '0' in profile['games'] and 'name' in profile['games']['0']
    sh = '1' in profile['games'] and 'name' in profile['games']['1']
    if not sw and not sh:
        return False, f'WF_NO_IGN'

    return True, None


def ign_as_text(profile, delimeter='\n'):
    text = '✨ **IGN**: Not Set!'
    if not profile or 'games' not in profile:
        return text

    games = []
    if '0' in profile['games'] and 'name' in profile['games']['0'] and profile['games']['0']['name']:
        games.append(f"{EMOJI['sword']} **IGN**: {profile['games']['0']['name']}")

    if '1' in profile['games'] and 'name' in profile['games']['1'] and profile['games']['1']['name']:
        games.append(f"{EMOJI['shield']} **IGN**: {profile['games']['1']['name']}")

    if not games:
        return text

    return delimeter.join(games)


def fc_as_text(profile):
    fc = f"SW-{profile['friend_code']}" if profile['friend_code'] else 'Not set!'
    switch = profile['switch_name'] if profile['switch_name'] else 'Not set!'

    return f'''**🗺️ FC**: {fc}
{ign_as_text(profile)}
**🎮 Switch Name**: {switch}'''


class Trainers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.userdb = bot.trainerdb
        self.wfcache = {}

    '''
    wf profile
    '''



def setup(bot):
    trainers = Trainers(bot)
    bot.add_cog(trainers)
    bot.trainers = trainers
