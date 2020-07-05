
import re
import sys
import traceback

import discord

from datetime import datetime, timedelta

idPattern = re.compile(r'<@!?(\d+?)>')
cn_id_pattern = re.compile(r'<#([0-9]+)>')
emojiPattern = u'(?:[\U00002600-\U000027BF])|(?:[\U0001f300-\U0001f64F])|(?:[\U0001f680-\U0001f6FF])'
customEmojiPattern = r'<.?:(?:.+?):(?:\d+?)>'

ERROR_RED = 0xD32F2F
INFO_BLUE = 0x3579f0

DBL_BREAK = '\n \n'
FIELD_BREAK = '\n\u200b'

TYPE_COLORS = (
    0xFFFFFF,
    0xE88158,
    0x57AADE,
    0x7FBF78,
    0x9C6E5A,
    0xF2CB6F,
    0x9DD1F2,
    0xAD70D5,
    0xF0A1C1,
    0x222222,
    0x646EAB
)

ICON_ATTACK = '⚔'
ICON_CLOSE = '❌'
BLUE_HEART = '💙'
GREEN_HEART = '💚'
YELLOW_HEART = '💛'
SPY_EMOJI = '🕵️'



def strip_extra(s):
    return re.sub('[^\sA-Za-z]+', '', s)


def normalize(s):
    return s.lower().strip().replace(' ', '')

def pluralize(word, val):
    return word if val == 1 else f'{word}s'

def simplify_timedelta(d):
    if d.days > 0:
        return f'''{int(d.days)} **{pluralize('day', d.days)}**'''
    if d.seconds > 3600:
        hours = d.seconds // 3600
        return f'''{int(hours)} **{pluralize('hour', hours)}**'''
    if d.seconds > 60:
        mins = d.seconds / 60
        return f'''{int(mins)} **{pluralize('min', mins)}**'''

    return f'''{int(d.seconds)} **{pluralize('second', d.seconds)}**'''


class MemberNotFound(Exception):
    pass


def resolve_member(server, member_id):
    member = server.get_member(member_id)
    if member is None:
        raise MemberNotFound()
        # if server.chunked:
        #     raise MemberNotFound()
        # try:
        #     member = await server.fetch_member(member_id)
        # except discord.NotFound:
        #     raise MemberNotFound() from None
    return member


def find_members(bot, server, query, get_ids=False):
    if not query:
        return None

    uid = None
    match = re.search(r'\b\d+?\b', query)
    if match:
        uid = int(match.group(0))

    match = idPattern.search(query)
    if match:
        uid = int(match.group(1))

    if uid is not None:
        if get_ids:
            return [uid]
        try:
            member = resolve_member(server, uid)
            return [member]
        except MemberNotFound:
            # hackban case
            return [discord.Object(id=uid)]

    found = {}
    query = normalize(query)
    for m in server.members:
        if query == str(m.id) or normalize(str(m)).startswith(query) or query in normalize(m.name) or (m.name and m.nick and query in normalize(m.nick)):
            found[m.id] = m



    return list(found.keys()) if get_ids else list(found.values())


def get_member_or_search(bot, server, query):
    found = find_members(bot, server, query)

    if found and len(found) == 1:
        return True, found[0]

    return False, whois_text(found, show_extra=False)


def whois_text(found, show_extra=True):
    if not found:
        return 'No matching users found.'

    now = datetime.utcnow()
    out = []
    for m in found:
        parts = [f'<@{m.id}>', str(m)]
        if m.nick:
            parts.append(f'Nickname: {m.nick}')
        parts.append(str(m.id))

        if show_extra and m.joined_at and m.created_at:
            joined_ago = now - m.joined_at
            created_ago = now - m.created_at
            parts.append(f'Joined: {simplify_timedelta(joined_ago)} ago')
            parts.append(f'Created: {simplify_timedelta(created_ago)} ago')

            if m.joined_at - m.created_at < timedelta(minutes=15):
                parts.append('⚠ **Joined within 15 minutes of making an account.**')

        out.append('\n'.join(parts))

    out = DBL_BREAK.join(out)
    if(len(found) > 1):
        out = f'_Multiple members found:_{DBL_BREAK}{out}'

    if len(out) > 1997:
        out = out[:1997] + '...'

    return out


async def send_message(ctx, text, message=None, ping=True, error=False, color=None, image_url=None, expires=None):

    message = message or ctx.message

    if(error):
        text = f"ERROR: {text}"

    e = discord.Embed(description=text)
    if color or error:
        e.color = color if color else ERROR_RED
    if expires is None and error:
        expires = 10
    if image_url is not None:
        e.set_image(url=image_url)

    header = '<@{}>'.format(message.author.id) if ping else ''
    sent = await message.channel.send(header, embed=e, delete_after=expires)
    return sent


async def send_user_not_found(ctx, arg):
    await send_message(ctx, f'''Couldn't find a trainer in this server by that name!''', error=True)


def enquote(text):
    return f'“{text}”'


def ordinal(num, bold=False):
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
    return "**{}**{}".format(num, suffix) if bold else str(num) + suffix


def clamp(n, lo, hi):
    return max(min(n, hi), lo)


def print_error(ctx, error):
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    pass




