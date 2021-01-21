import discord
import datetime

async def dump_all(bot):
    koop_guild_id = 372482304867827712
    koop_guild = bot.get_guild(koop_guild_id)

    # for channel in wg_guild.text_channels:
    #     if '_' in channel.name:
    #         renamed = channel.name.replace('_', '-')
    #         print(f'renaming {channel.name} to {renamed}')
    #         await channel.edit(name=renamed)
    for role in koop_guild.roles:
        print(f"{role.id}, #{role}")


# async def make_holding_server(bot):
    # guild = await bot.create_guild('KO_OP Appeals Server') #, code='BkgCzhH9CNQ2')
    # print(guild, guild.id)

    # guild = bot.get_guild(732129494957162507)
    # invite = await guild.text_channels[0].create_invite()
    # print(invite, invite.url)

#
# async def add_admin_holding_server(bot):
#     guild = bot.get_guild(732129494957162507)
#     role = await guild.create_role(name='admin', permissions=discord.Permissions.all(), hoist=True)
#     # role = guild.get_role(id)
#     m = guild.get_member(232650437617123328)
#     await m.add_roles(role)


async def add_role_to_everyone_before_minutes(bot, minutes):
    koop_guild_id = 372482304867827712
    koop_guild = bot.get_guild(koop_guild_id)


    role = koop_guild.get_role(798994054695747645)

    time = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
    n = 0
    total = len(koop_guild.members)
    for m in koop_guild.members:
        n += 1
        if m.joined_at < time:
            if role in m.roles:
                print(f'{m} already has role [{n}/{total}]')
                continue

            print(f'adding to {m} [{n}/{total}]')
            await m.add_roles(role)
            print(f'added to {m} [{n}/{total}]')

    print('done')