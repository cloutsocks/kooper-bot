from discord.ext import commands

async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    async def predicate(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(predicate)


async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_guild_permissions(*, check=all, **perms):
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=check)
    return commands.check(predicate)

# These do not take channel overrides into account


def is_jacob():
    def predicate(ctx):
        return ctx.message.author.id in ctx.bot.config['creator_ids']
    return commands.check(predicate)


def is_mod():
    async def predicate(ctx):
        return await check_guild_permissions(ctx, {'manage_guild': True})
    return commands.check(predicate)


def check_bot_admin(member, bot):
    return member.id in bot.config['admin_ids'] or \
           member.guild_permissions.administrator or \
           any(role in member.roles for role in bot.raid_cog.admin_roles)


def is_bot_admin():
    async def predicate(ctx):
        return check_bot_admin(ctx.author, ctx.bot)
    return commands.check(predicate)


def is_wooloo_staff():
    async def predicate(ctx):
        return ctx.author.id in ctx.bot.config['wooloo_staff_ids']
    return commands.check(predicate)


def mod_or_permissions(**perms):
    perms['manage_guild'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)


def admin_or_permissions(**perms):
    perms['administrator'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids
    return commands.check(predicate)


def is_wooloo_farm():
    return is_in_guilds(649042459195867136, 660997103014903818)
