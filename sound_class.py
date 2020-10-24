import os
import youtube_dl
from pathlib import Path
from tinydb import TinyDB, Query
from config import Config


class SoundFile:
    def __init__(self, guild, command_name=None, url=None, title=None):
        self.command_name = command_name
        self.url = url
        self.guild = guild
        self.guild_id = guild.id
        self.config = Config(guild)
        self.path = Path.cwd() / 'sounds'
        if not self.path.is_dir():
            self.path.mkdir()

        if title:
            self.title = title
        else:
            self.title = '%(title)s'

        self.file_path = self.path / self.title
        self.db_path = self.path / f'sounds_{self.guild_id}.json'

        self.ydl_opts = {'format': 'bestaudio',
                         'noplaylist': True,
                         'outtmpl': f'{self.file_path}.%(ext)s',
                         'postprocessors': [{'key': 'FFmpegExtractAudio'}]}

        self.db = TinyDB(self.db_path)
        self.config.sounds = self.db_path
        self.config.update_config()

    def download_sound(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        for file in self.path.iterdir():
            breakpoint()
            if file.stem == self.file_path.stem:
                self.file_path.rename(file(file.suffix))

        self.add_command()

    def add_command(self):
        config = Config(self.guild)
        command_info = {'file': self.file_path,
                        'command_name': str(self.command_name)}

        self.db.insert(command_info)
        config.update_config()

    def view_commands(self):
        for command in self.db:
            print(command)
