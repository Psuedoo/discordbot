import os


def is_mod(ctx):
    return ctx.message.author.is_mod == 1


def is_psuedo(ctx):
    return ctx.message.author.name == "Psuedo"

def is_bot_enabled(ctx):
    roles = ctx.message.author.roles
    for role in roles:
        if role.name == "Bot Enabled":
            bot_enabled_role = role
    return bot_enabled_role
    

