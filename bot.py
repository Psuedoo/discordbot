import os
import discord
import asyncio
import db.db_handler
from db.db_handler_command import get_command_names, get_response
from discord.ext import commands

token = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.members = True


initial_extensions = ["cogs.basic",
                      "cogs.admin",
                      "cogs.sound",
                      "cogs.command",
                      "cogs.streamer",
                      "cogs.role",
                      "cogs.poll"]

# TODO: Change commands from file usage -> DB
#           - Get/Set Prefix in DB


async def prefix(bot, message):
    guild = message.channel.guild
    return await db.db_handler.get_prefix(guild)


global bot
bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)
bot.owner_id = 266388033631158273


async def handle_echo(reader, writer):
    data = await reader.read(100)
    message = data.decode()

    await vctest(message, bot.voice_clients)

    print(f"Received {message!r}.")

    await writer.drain()

    print("Close the connection")
    writer.close()


async def socket_main():
    server = await asyncio.start_server(handle_echo, 'localhost', 4000)

    async with server:
        await server.serve_forever()


@bot.event
async def on_ready():
    print("Logged in")
    await db.db_handler.initialize_guilds(bot.guilds)

    # TODO : Once converted bot into class, make presence setting command
    game = discord.Game("operating on myself")
    await bot.change_presence(status=discord.Status.online, activity=game)
    await socket_main()


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    else:
        command_names = await get_command_names(message.guild)
        guild_prefix = await prefix(bot, message)
        if message.content.startswith(guild_prefix) and message.content[1:] in command_names:
            response = await get_response(message.guild, message.content[1:])
            await message.channel.send(response[0])
        else:
            await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f"Welcome {member.mention} to {guild.name}!"
        await guild.system_channel.send(to_send)


@bot.command(name="help")
async def help_command(ctx, specific_help=None):
    def build_cog_embed(cogs, specific_cog=None):
        embeds = []
        for cog in cogs.values():
            if not cog.hidden:

                cog_embed = discord.Embed(title=f'**__{cog.qualified_name} Commands__**',
                                          description=cog.description)
                for command in cog.get_commands():
                    if not command.hidden:
                        if len(command.clean_params) > 0:
                            parameters = [f"<{param}>" for param in command.clean_params.keys()]

                        value = (f'__About__:\n{command.description}\n\n'
                                 f'__Usage__:\n{prefix}{command.qualified_name} {" ".join(parameters)}')

                        if len(command.aliases) > 0:
                            value += f'\n\n__Aliases__:\n{command.aliases}'

                        cog_embed.add_field(name=command.name, value=value)
                embeds.append(cog_embed)

        if specific_cog:
            return [embed for embed in embeds if specific_cog.lower() in embed.title.lower()]
        else:
            return embeds

    prefix = await bot.get_prefix(ctx.message)
    embed_top = discord.Embed(title="Help",
                              description="PsuedooBot Command Help",
                              author="Psuedo#2187")
    if not specific_help:
        embed_list = build_cog_embed(ctx.bot.cogs)
    else:
        embed_list = build_cog_embed(ctx.bot.cogs, specific_help)

    embed_list.insert(0, embed_top)

    if len(embed_list) > 1:
        for embed in embed_list:
            await ctx.author.send(content=None, embed=embed)

    elif len(embed_list) > 1 and specific_help:
        await ctx.send(f"Nothing was found with {specific_help}")


@bot.command(name="test", hidden=True)
async def test(ctx):
    await ctx.send(f"The test has passed!")


@bot.command(name="vctest", hidden=True)
async def vctest(message, clients):
    print(message)
    tags = message.split(";")
    print(tags)
    sound_name = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("sound_name=")][0]
    channel_name = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("channel_name=")][0]
    discord_id = [tag[tag.find("=") + 1:] for tag in tags if tag.startswith("discord_id=")][0]

    async def play_sound(bot, clients, discord_id):
        sound_cog = bot.get_cog('Sound')
        for client in clients:
            if int(discord_id) == client.guild.id:
                await sound_cog.sound_handler(sound_name, discord_id, client)
                return
            elif int(discord_id) != client.guild.id:
                continue
            else:
                print("Some error with vctest")

        clients.append(await sound_cog.join(discord_id=discord_id))
        await play_sound(bot, clients, discord_id)
        return

    await play_sound(bot, clients, discord_id)


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
