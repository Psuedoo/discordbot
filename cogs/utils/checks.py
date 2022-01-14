def is_mod(ctx):
    return 'Mod' in [role.name for role in ctx.author.roles]