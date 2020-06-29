import random


async def tally(bot, channel_id, cap=30):
    channel = bot.get_channel(channel_id)
    tallies = []
    async for message in channel.history(limit=None):
        try:
            n = int(message.content)
        except ValueError:
            print(f'Skipped {message.content}')
            continue
        tallies.append((str(message.author), n))

    # for t in tallies:
    #     donor, n = t
    #     if n > cap:
    #         print(f'{cap} (capped from {n}) from {donor}')
    #     else:
    #         print(f'{n} from {donor}')
    #
    # total = sum(min(30, t[1]) for t in tallies)
    # print(f'-----\n{total} total')

    for t in tallies:
        donor, n = t
        print(f'{n}, {donor}')

    # total = sum(min(30, t[1]) for t in tallies)
    # print(f'-----\n{total} total')

async def raffle(bot):

    # channel = bot.get_channel(680310582083452932)
    # donor_stock = {}
    # donor_list = []
    # assigned = {}
    # id_to_name = {}
    # async for message in channel.history(limit=None):
    #     try:
    #         n = int(message.content)
    #     except ValueError:
    #         print(f'Skipped {message.content}')
    #         continue
    #     donor_stock[message.author.id] = n
    #     donor_list.append(message.author.id)
    #     assigned[message.author.id] = []
    #     id_to_name[message.author.id] = str(message.author)
    #
    #
    channel = bot.get_channel(677590139551350835)
    msg = await channel.fetch_message(677591719549730827)

    reactions = []
    for reaction in msg.reactions:
        users = await reaction.users().flatten()
        reactions.append(users)

    cool = []
    why = []
    for u in reactions[0] + reactions[1]:
        # if u.id in donor_list:
        #     continue

        if u in reactions[0] and u in reactions[1]:
            if u not in cool:
                cool.append(u)
        else:
            if u not in why:
                why.append(u)

    role = channel.guild.get_role(680950022136791124)
    for u in cool:
        if u in channel.guild.members:
            print(f'adding to {str(u)}')
            await u.add_roles(role)
            print(f'added to {str(u)}')

    # draws = random.sample(cool, 20)
    # for u in draws:
    #     if u in channel.guild.members:
    #         print(str(u))

    # i = 0
    # for u in cool:
    #     while donor_stock[donor_list[i]] == 0:
    #         del donor_list[i]
    #         if i >= len(donor_list):
    #             i = 0
    #     assigned[donor_list[i]].append(str(u))
    #     donor_stock[donor_list[i]] -= 1
    #     i += 1
    #     if i >= len(donor_list):
    #         i = 0
    #
    # for key in assigned:
    #     donor = id_to_name[key]
    #     for user in assigned[key]:
    #         print(f'{donor}|{user}')





    # print('cool\n', ' '.join([str(u) for u in cool]))
    # print('\nwhy\n', ' '.join([str(u) for u in why]))
    #
    # print('\n\n', ' '.join([f'<@{u.id}>' for u in why]))


async def get_test_raid_members(bot, limit=200):
    channel = bot.get_channel(652367800912052244)
    members = []
    async for message in channel.history(limit=limit):
        if message.author in channel.guild.members:
            members.append(message.author)
    print(', '.join([str(m.id) for m in members]))
    return members
