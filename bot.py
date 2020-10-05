
import os
import json
import discord
import requests
from pathlib import Path
from discord.ext import commands


TOKEN = os.environ['TOKEN']
GUILD = os.environ['DISCORD_GUILD']

token=os.environ["TOKEN"]
guild=os.environ["DISCORD_GUILD"] 

# client = discord.Client()


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='?', intents=intents)

initial_extensions = ["cogs.basic","cogs.admin"]

@bot.event
async def on_ready():
    print(f"Logged in")

    # TODO : Make it where config doesn't get overwritten by defaults.
    # need to keep the default in a default config to compare to the edited one then to set the value to false

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
        default_config_dict = {'owner_id': guild.owner.id,
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

@bot.command(name="emoji")
async def emoji(ctx):
    print(bot.get_emoji(1))

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(token)
