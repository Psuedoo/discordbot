from pathlib import Path
from tinydb import TinyDB, Query
from config import Config
from cogs.utils import checks
from discord.ext import commands


def instantiate_configs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return Config(guild)

    else:
        return [Config(guild) for guild in guilds]


def instantiate_dbs(guilds, specific_guild_id=None):
    if specific_guild_id:
        for guild in guilds:
            if guild.id == specific_guild_id:
                return TinyDB(Config(guild).sounds)

    else:
        return [TinyDB(Config(guild).sounds) for guild in guilds]


class CustomCommandClass:
    def __init__(self, guild):
        self.guild_id = guild.id
        self.config = Config(guild)
        self.path = Path.cwd() / 'commands'
        if not self.path.is_dir():
            self.path.mkdir()
        self.db_path = self.path / f'commands_{self.guild_id}.json'
        self.db = TinyDB(self.db_path)
        self.config.commands = self.db_path
        # p = Path('~')
        # self.path = p / 'coding' / 'commands'
        # self.db = TinyDB(f'{os.path.expanduser(self.path)}/commands_{self.guild_id}.json')
        # self.config.commands = f"{os.path.expanduser(self.path)}/commands_{self.guild_id}.json"
        self.config.update_config()

    def handle_command(self, message):
        Command = Query()
        command = message.content[1:]
        try:
            response = self.db.search(Command.command_name == command)[0]
            return response.get('command_response')
        except:
            return None

    def add_custom_command(self, command_name, command_response):
        if command_name and command_response:
            self.db.insert({'command_name': command_name, 'command_response': command_response})
        else:
            return

    def delete_custom_command(self, command_name):
        Command = Query()
        table = self.db.table('_default')

        try:
            command = [command.get('file') for command in self.db if command.get('command_name') == command_name][0]
        except IndexError as e:
            return "Sound doesn't exist"

        try:
            table.remove(Command.command_name == command_name)
        except:
            return f"Failed to delete {command_name} sound."
        else:
            return f"Successfully deleted {command_name} sound!"

    def view_custom_commands(self):
        commands = [command.get('command_name') for command in self.db.all()]
        return commands


class CustomCommand(commands.Cog):
    """*Commands regarding custom commands*"""
    def __init__(self, bot):
        self.bot = bot
        self.guilds = self.bot.guilds

    @commands.command(name="addcommand", description="Adds a custom command")
    @commands.check(checks.is_bot_enabled)
    async def add_custom_command(self, ctx, command_name, command_response):
        cc = CustomCommandClass(ctx.guild)
        cc.add_custom_command(command_name, command_response)
        await ctx.send(f"Successfully added {command_name}!")

    @commands.command(name="deletecommand", description="Deletes a custom command")
    @commands.check(checks.is_bot_enabled)
    async def delete_custom_command(self, ctx, command_name):
        cc = CustomCommandClass(ctx.guild)
        cc.delete_custom_command(command_name)
        await ctx.send(f"Successfully deleted {command_name}!")

    @commands.command(name="viewcommands", description="Displays the custom commands")
    async def view_custom_commands(self, ctx):
        cc = CustomCommandClass(ctx.guild)
        await ctx.send(cc.view_custom_commands())


def setup(bot):
    bot.add_cog(CustomCommand(bot))
