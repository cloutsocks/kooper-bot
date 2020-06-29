

async def replace_underscores(bot):
    wg_guild_id = 546468613805309962
    wg_guild = bot.get_guild(wg_guild_id)

    for channel in wg_guild.text_channels:
        if '_' in channel.name:
            renamed = channel.name.replace('_', '-')
            print(f'renaming {channel.name} to {renamed}')
            await channel.edit(name=renamed)


async def add_role_to_everyone(bot):
    wg_guild_id = 546468613805309962
    wg_guild = bot.get_guild(wg_guild_id)

    role = wg_guild.get_role(675405122066579468)


    for m in wg_guild.members:
        print(f'adding to {str(m)}')
        await m.add_roles(role)
        print(f'added to {str(m)}')

    print('done')