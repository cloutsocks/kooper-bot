from pprint import pprint
from common import FIELD_BREAK

async def tally_reactions(bot, emoji, channel_id, limit=None):
    channel = bot.get_channel(channel_id)
    out = bot.get_channel(732399348289110088)
    tallies = []
    async for msg in channel.history(limit=limit):
        for reaction in msg.reactions:
            if str(reaction.emoji) == emoji:
                tallies.append((reaction.count, msg.author, msg.attachments[0].url))
                continue

    role = channel.guild.get_role(679074193677221889)

    tallies.sort(key=lambda entry: entry[0], reverse=True)
    for i, entry in enumerate(tallies):
        votes, member, url = entry
        if member in channel.guild.members:
            print(f'adding to {str(member)}')
            await member.add_roles(role)
            print(f'added to {str(member)}')

        if i < 3:
            extra = ['🥇 _1st Place_',
                     '🥈 _2nd Place_',
                     '🥉 _3rd Place_',][i]
        elif i < 30:
            extra = f'_#{i+1}_'
        else:
            extra = '_Honorable Mention_'

        s = f'''{FIELD_BREAK}
{extra}
<@{member.id}> / {member}
{url}
**{votes}** votes'''
        # await out.send(s)