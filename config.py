import os
import json
from pathlib import Path

class Config:
    def __init__(self, guild):
        self.path = Path('.') / 'configs' / f'{guild.id}_config.json'
        if self.path.is_file():
            config_data = self.get_config()
        else:
            config_data = {}

        self.prefix = config_data.get('prefix', '?')
        self.guild_name = config_data.get('guild_name', guild.name)
        self.guild_id = config_data.get('guild_id', guild.id)
        self.owner_id = config_data.get('owner_id', guild.owner.id)
        self.streamer_id = config_data.get('streamer_id', None)
        self.streamer_announcement_channel_id = config_data.get('streamer_announcement_channel_id', None)
        self.streamers = config_data.get('streamers', {})
        roles = {}
        for role in guild.roles:
            roles[role.id] = {'name': role.name,
                            'emoji': None}
        self.roles = config_data.get('roles', roles)
        self.role_message_id = config_data.get('role_message_id', None)
        self.role_message_channel_id = config_data.get('role_message_channel_id', None)
        self.sounds = config_data.get('sounds', None)
        self.commands = config_data.get('commands', None)
        
        if len(config_data) == 0:
            self.update_config()

    def to_json(self):
        property_dict = {
                "prefix": self.prefix,
                "guild_name": self.guild_name,
                "guild_id": self.guild_id,
                "owner_id": self.owner_id,
                "streamer_id": self.streamer_id,
                "streamer_announcement_channel_id": self.streamer_announcement_channel_id,
                "streamers": self.streamers,
                "roles": self.roles,
                "role_message_id": self.role_message_id,
                "role_message_channel_id": self.role_message_channel_id,
                "sounds": self.sounds,
                "commands": self.commands
                }
        return json.dumps(property_dict, indent=2)


    def create_config(self):
        if self.config_file_path.is_file():
            print(f"{self.config_file_path} already exists.")
            return None

        else:
            print(f"Created {self.config_file_path}")
            self.update_config()
    
    def update_config(self):
        with open(self.path.absolute(), "w") as config_file:
            config_file.write(self.to_json())

    def get_config(self):
        try:
            with open(self.path.absolute()) as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            self.update_config()
