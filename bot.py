import os
import json
import discord
import requests
from cogs.utils import checks
from pathlib import Path
from discord.ext import commands


TOKEN = os.environ['TOKEN']
GUILD = os.environ['DISCORD_GUILD']

token=os.environ["TOKEN"]
guild=os.environ["DISCORD_GUILD"] 

intents = discord.Intents.default()
intents.members = True

initial_extensions = ["cogs.basic","cogs.admin"]

def get_configs(bot):
    guild_configs = {} 

    for guild in bot.guilds:

        with open(f'configs/{guild.id}_config.json') as f:
            data = json.load(f)
            guild_configs[guild.id] = data
    return guild_configs

def prefix(bot, message):
    id = message.channel.guild.id
    configs = get_configs(bot)
    prefix = configs[id]['prefix']
    return prefix 


bot = commands.Bot(command_prefix=prefix, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in")


    config_path = "~/coding/discordbot/configs"
    response = requests.get("https://gist.githubusercontent.com/oliveratgithub/0bf11a9aff0d6da7b46f1490f86a71eb/raw/d8e4b78cfe66862cf3809443c1dba017f37b61db/emojis.json")
    
    gross_emoji_list = response.json()['emojis']
    gross_emoji_list = gross_emoji_list[24:275]
    emoji_list = []
    
    for emoji in gross_emoji_list:
        emoji_list.append(emoji['shortname'])

    for guild in bot.guilds:
        # Maybe exclude the admin roles if you can see perms?
        # Don't want to be able to assign yourself an admin role with choosing an emoji
        roles = []
        for role in guild.roles:
            roles.append({'name': role.name, 'role_id': role.id})
        default_config_dict = {'prefix': '?',
                                'owner_id': guild.owner.id,
                                'roles': roles,
                                'role_message_id': None,
                                'role_message_channel_id': None,
                                'emojis': emoji_list,
                            }
        
        default_config_json = json.dumps(default_config_dict, indent=2)
        # ~/coding/discordbot/configs/guild.id_config.json 
        config_file = Path(f"configs/{guild.id}_config.json")
        if config_file.is_file():
            print(f"{guild.id}'s config already exists.")
            continue

        else:
            with open(config_file, "w") as fp:
                fp.write(default_config_json)

            print(f"Created config for: {guild.id}")



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
    configs = get_configs(ctx.bot)
    current_config = configs[guild_id]
    current_config['prefix'] = str(prefix)
    with open(f"configs/{guild_id}_config.json", "w") as config_file:
        config_file.write(json.dumps(current_config, indent=2))
    await ctx.send(f"Prefix has been updated to {prefix}")

@bot.command(name="emoji")
async def emoji(ctx):
    print(bot.get_emoji(1))

@bot.command(name="roles")
async def roles(ctx):
    roles = ctx.author.roles
    print(f"{roles}")


if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
