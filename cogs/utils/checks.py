import os


def is_mod(ctx):
    return ctx.message.author.is_mod == 1


def is_psuedo(ctx):
    return ctx.message.author.name == "Psuedo"


