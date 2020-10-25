import os
import json
from pathlib import Path


class Config:
    def __init__(self, guild):
        self.folder_path = Path.cwd() / 'configs'

        if not self.folder_path.is_dir():
            self.folder_path.mkdir()

        self.path = self.folder_path / f'{guild.id}_config.json'

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
        self.sounds =  Path.cwd() / 'sounds' / f'sounds_{self.guild_id}.json'
        self.commands = Path.cwd() / 'commands' / f'commands_{self.guild_id}.json'

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
            "sounds": str(self.sounds),
            "commands": str(self.commands),
        }
        return json.dumps(property_dict, indent=2)

    def update_config(self):
        with open(self.path.absolute(), "w") as config_file:
            config_file.write(self.to_json())

    def get_config(self):
        try:
            with open(self.path) as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            self.update_config()
