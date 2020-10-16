import os
import youtube_dl
from pathlib import Path
from tinydb import TinyDB, Query


class SoundFile:
    def __init__(self, command_name, url, title=None):
        self.command_name = command_name
        self.url = url
        if title:
            self.title = title
        else:
            self.title = '%(title)s'


        self.ydl_opts = {'format': 'bestaudio',
                        'noplaylist': True,
                        'outtmpl': f'~/coding/sounds/{self.title}.%(ext)s',
                        'postprocessors': [{'key': 'FFmpegExtractAudio'}]}
         
        
        p = Path('~')
        self.path = p / 'coding' / 'sounds'
        self.file_path = f'~/coding/sounds/{self.title}'

        self.db = TinyDB(f'{os.path.expanduser(self.path)}/sounds.json')
        

    def download_sound(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

        if os.path.isfile(os.path.expanduser(self.file_path)+'.m4a'):
            extension = '.m4a'
        elif os.path.isfile(os.path.expanduser(self.file_path)+'.opus'):
            extension = '.opus'
        elif os.path.isfile(os.path.expanduser(self.file_path)+'.ogg'):
            extension = '.ogg'
        elif os.path.isfile(os.path.expanduser(self.file_path)+'.mp3'):
            extension = '.mp3'
        else:
            extension = '.savingasdiffext'
 
        self.file_path = self.file_path+extension

        self.add_command()

    def add_command(self):
        command_info = {'file': self.file_path,
                        'command_name': str(self.command_name)}

        self.db.insert(command_info)

    def view_commands(self):
        for command in self.db:
            print(command)
            
if __name__ == '__main__':
    command_name = input("Enter a command name: ")
    url = input("Please enter a url: ")
    title = input("Please enter a title, or N: ")

    if title.lower() != "n":
        sound = SoundFile(command_name, url, title)
    else:
        sound = SoundFile(command_name, url)

    sound.download_sound()

    sound.view_commands()

