import youtube_dl


class SoundFile:
    def __init__(self, url, title=None):
        self.url = url
        if title:
            self.title = title
        else:
            self.title = '%(title)s'

        self.ydl_opts = {'format': 'bestaudio',
                        'outtmpl': f'{self.title}.%(ext)s',
                        'postprocessors': [{'key': 'FFmpegExtractAudio'}]}

    def download_sound(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([self.url])

