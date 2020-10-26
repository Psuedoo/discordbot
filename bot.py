import os
import discord
import asyncio
from config import Config
from cogs.command import CustomCommandClass
from cogs.utils import checks
from discord.ext import commands

token = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.members = True

initial_extensions = ["cogs.basic",
                      "cogs.admin",
                      "cogs.sound",
                      "cogs.command",
                      "cogs.streamer",
                      "cogs.role"]


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()

    await vctest(message)

    print(f"Received {message!r}.")

    await writer.drain()

    print("Close the connection")
    writer.close()


async def socket_main():
    server = await asyncio.start_server(handle_echo, 'localhost', 4000)

    async with server:
        await server.serve_forever()


def prefix(bot, message):
    id = message.channel.guild.id
    configs = [Config(guild) for guild in bot.guilds]

    for config in configs:
        if config.guild_id == id:
            return config.prefix


bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
bot.owner_id = 266388033631158273


@bot.event
async def on_ready():
    print("Logged in")
    configs = [Config(guild) for guild in bot.guilds]

    for config in configs:
        print(config.guild_id)

    # TODO : Once converted bot into class, make presence setting command
    game = discord.Game("operating on myself")
    await bot.change_presence(status=discord.Status.online, activity=game)
    await socket_main()


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        commands = CustomCommandClass(message.guild)
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


@bot.command(name="help")
async def help_command(ctx):
    prefix = await bot.get_prefix(ctx.message)
    embed_top = discord.Embed(title="Help",
                              description="PsuedooBot Command Help",
                              author="Psuedo#2187")
    embeds = [embed_top]
    for cog in bot.cogs.values():
        cog_embed = discord.Embed(title=f'**__{cog.qualified_name} Commands__**',
                                  description=cog.description)
        for command in cog.get_commands():
            if not command.hidden:

                value = f'__About__:\n{command.description}\n\n__Usage__:\n{command.usage}'

                if len(command.aliases) > 0:
                    value += f'\n\n__Aliases__:\n{command.aliases}'

                cog_embed.add_field(name=command.name, value=value)
        embeds.append(cog_embed)

    for embed in embeds:
        await ctx.author.send(content=None, embed=embed)


@bot.command(name="test")
async def test(ctx):
    await ctx.send("The test has passed!")


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
