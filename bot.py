import os
import discord
import asyncio
from config import Config
from command_class import CustomCommand
from cogs.utils import checks
from discord.ext import commands

token = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.members = True

initial_extensions = ["cogs.basic",
                      "cogs.admin",
                      "cogs.sound",
                      "cogs.command",
                      "cogs.streamer"]


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()

    await vctest(message)

    print(f"Received {message!r}.")

    await writer.drain()

    print("Close the connection")
    writer.close()


async def socket_main():
    server = await asyncio.start_server(handle_echo, 'localhost', 3000)

    async with server:
        await server.serve_forever()


def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        configs = []
        for guild in guilds:
            configs.append(Config(guild))
        return configs


def prefix(bot, message):
    id = message.channel.guild.id
    configs = instantiate_configs(bot.guilds)

    for config in configs:
        if config.guild_id == id:
            return config.prefix


bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.event
async def on_ready():
    print("Logged in")
    configs = instantiate_configs(bot.guilds)

    for config in configs:
        print(config.guild_id)

    await socket_main()


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        commands = CustomCommand(message.guild)
        guild_prefix = prefix(bot, message)
        if message.content.startswith(guild_prefix) and message.content[1:] in commands.view_custom_commands():
            await message.channel.send(commands.handle_command(message))
        else:
            await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.mention} to {guild.name}!"
        await guild.system_channel.send(to_send)


@bot.command(name="test")
async def test(ctx):
    await ctx.send("The test has passed!")


@commands.check(checks.is_bot_enabled)
@bot.command(name="setprefix")
async def set_prefix(ctx, prefix):
    guild_id = ctx.message.channel.guild.id
    current_config = instantiate_configs(ctx.bot.guilds, guild_id)
    current_config.prefix = str(prefix)
    current_config.update_config()
    await ctx.send(f"Prefix has been updated to {prefix}")


@bot.command(name="vctest")
async def vctest(message, ctx=None):
    print(message)
    tags = message.split(";")
    print(tags)
    sound_name = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("sound_name=")][0]
    channel_name = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("channel_name=")][0]
    discord_id = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("discord_id=")][0]
    sound = bot.get_cog('Sound')
    await sound.join(None, channel_name, discord_id)
    await sound.sound_handler(sound_name, discord_id)


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
