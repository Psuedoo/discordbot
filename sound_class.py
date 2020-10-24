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
        if title:
            self.title = title
        else:
            self.title = '%(title)s'

        self.ydl_opts = {'format': 'bestaudio',
                         'noplaylist': True,
                         'outtmpl': f'~/coding/sounds/{self.title}.%(ext)s',
                         'postprocessors': [{'key': 'FFmpegExtractAudio'}]}

        self.path = Path.cwd() / 'sounds'
        # self.file_path = f'~/coding/sounds/{self.title}'
        self.file_path = f'{self.file_path}/{self.title}'
        self.db.path = f'{self.path}/sounds_{self.guild_id}.json'

        self.db = TinyDB(self.db.path)
        self.config.sounds = self.db.path
        self.config.update_config()

    def download_sound(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        if os.path.isfile(os.path.expanduser(self.file_path) + '.m4a'):
            extension = '.m4a'
        elif os.path.isfile(os.path.expanduser(self.file_path) + '.opus'):
            extension = '.opus'
        elif os.path.isfile(os.path.expanduser(self.file_path) + '.ogg'):
            extension = '.ogg'
        elif os.path.isfile(os.path.expanduser(self.file_path) + '.mp3'):
            extension = '.mp3'
        else:
            extension = '.savingasdiffext'

        self.file_path = self.file_path + extension

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
