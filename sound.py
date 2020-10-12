import youtube_dl


class Sound:
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


if __name__ == '__main__':
    url = input("Please enter a url you want to download: ")
    title = input("Please input a title or N: ")
    if title.lower() == "n":
        sound = Sound(url, title=None)
    else:
        sound = Sound(url, title=title)

    sound.download_sound()
