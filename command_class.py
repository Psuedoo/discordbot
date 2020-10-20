import os
import youtube_dl
from pathlib import Path
from tinydb import TinyDB, Query
from config import Config


class CustomCommand:
    def __init__(self, guild):
        self.guild_id = guild.id
        self.config = Config(guild)
        p = Path('~')
        self.path = p / 'coding' / 'commands'
        self.db = TinyDB(f'{os.path.expanduser(self.path)}/commands_{self.guild_id}.json')
        self.config.commands = f"{os.path.expanduser(self.path)}/commands_{self.guild_id}.json"
        self.config.update_config()

    def handle_command(self, message):
        Command = Query()
        command = message.content[1:]
        response = self.db.search(Command.command_name == command)[0]
        return response.get('command_response')

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
           
