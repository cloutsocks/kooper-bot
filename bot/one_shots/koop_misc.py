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
