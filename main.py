import sys
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube, Search
import re
import requests
import unicodedata
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, TCON, TRCK, TPUB, TPE2
from moviepy.editor import AudioFileClip  # Importar moviepy para la conversión de audio

def slugify(value, allow_unicode=False):
    """
    Convierte una cadena a una versión ASCII y elimina caracteres no deseados
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

class SpotifyPlaylistDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initSpotify()
    
    def initUI(self):
        self.setWindowTitle("Spotify Playlist Downloader")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Enter Spotify Playlist URL:")
        layout.addWidget(self.label)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.downloadPlaylist)
        layout.addWidget(self.download_btn)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def initSpotify(self):
        """Inicializa la conexión con la API de Spotify"""
        self.auth_manager = SpotifyClientCredentials(client_id='d67481b0a3134e21a4870f42f4988bf3',
                                                     client_secret='a3bd5765d10a4b66991097d607e4cde9')
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

    def getPlaylistTracks(self, playlistUrl):
        playlistID = self.getPlaylistID(playlistUrl)
        tracks = []
        offset = 0
        limit = 50
        total = self.spotify.playlist_items(playlistID, limit=1)['total']
        while offset < total:
            results = self.spotify.playlist_items(playlistID, offset=offset, limit=limit)
            tracks.extend(self.extractTracks(results['items']))
            offset += limit
        return tracks

    def getPlaylistTitle(self, data):
        return data["name"]

    def getPlaylistID(self, url):
        return url.split('/')[-1]

    def extractTracks(self, items):
        tracks = []
        for item in items:
            track = item['track']
            name = track['name']
            artist = track['artists'][0]['name']
            album = track['album']['name']
            album_artist = track['album']['artists'][0]['name']
            release_date = track['album']['release_date']
            genre = track['album'].get('genres', [''])[0]
            track_number = track['track_number']
            total_tracks = track['album']['total_tracks']
            cover_url = track['album']['images'][0]['url']
            tracks.append((name, artist, album, album_artist, release_date, genre, track_number, total_tracks, cover_url))
        return tracks

    def createFolder(self, title):
        current_dir = os.getcwd()
        download_folder = "Downloads"
        download_folder_path = os.path.join(current_dir, download_folder)
        if not os.path.exists(download_folder_path):
            os.mkdir(download_folder_path)

        playlist_folder = title
        playlist_folder_path = os.path.join(download_folder_path, playlist_folder)
        if not os.path.exists(playlist_folder_path):
            os.mkdir(playlist_folder_path)

        return playlist_folder_path

    def downloadSong(self, index, title, songArtist, albumArtist, albumName, releaseDate, genre, trackNumber, totalTracks, coverUrl, videoUrl, folderRoute):
        youtube = YouTube(videoUrl)
        songTitle = f"{index:02d} {title} - {songArtist}"
        streams = youtube.streams.filter(only_audio=True)
        streams_with_abr = [(s, int(s.abr[:-4])) for s in streams if s.abr]
        streams_sorted = sorted(streams_with_abr, key=lambda s: s[1], reverse=True)
        stream = streams_sorted[0][0]

        downloadRoute = folderRoute
        if not os.path.exists(downloadRoute):
            os.makedirs(downloadRoute)

        webm_filenameStr = str(songTitle)
        webm_filename = slugify(webm_filenameStr) + '.webm'
        print(f"Downloading {webm_filename} ... \n")
        webm_path = os.path.join(downloadRoute, webm_filename)

        if os.path.exists(webm_path):
            print(f"{webm_filename} already exists. Skipping download.\n")
            return

        outSong = stream.download(output_path=downloadRoute, filename=webm_filename)

        # Convertir WebM a MP3
        mp3_filename = slugify(songTitle) + '.mp3'
        mp3_path = os.path.join(downloadRoute, mp3_filename)
        try:
            audio_clip = AudioFileClip(outSong)
            audio_clip.write_audiofile(mp3_path)
            audio_clip.close()
        except Exception as e:
            print(f"Error converting {webm_filename} to MP3: {e}")
            return

        os.remove(outSong)  # Eliminar el archivo WebM

        # Descargar la portada del álbum
        cover_data = None
        if coverUrl:
            try:
                response = requests.get(coverUrl)
                cover_data = response.content
            except Exception as e:
                print(f"Error downloading cover art: {e}")

        # Agregar metadatos al archivo MP3
        try:
            audio = MP3(mp3_path, ID3=ID3)
            if not audio.tags:
                audio.add_tags()

            audio.tags.add(TIT2(encoding=3, text=title))
            audio.tags.add(TPE1(encoding=3, text=songArtist))
            audio.tags.add(TALB(encoding=3, text=albumName))
            audio.tags.add(TDRC(encoding=3, text=releaseDate))
            audio.tags.add(TCON(encoding=3, text=genre))
            audio.tags.add(TRCK(encoding=3, text=f"{trackNumber}/{totalTracks}"))
            audio.tags.add(TPE2(encoding=3, text=albumArtist))
            if cover_data:
                audio.tags.add(APIC(
                    encoding=3, 
                    mime='image/jpeg', 
                    type=3, 
                    desc='Cover', 
                    data=cover_data
                ))
            audio.save()
        except HeaderNotFoundError:
            print(f"Error: {mp3_path} does not appear to be a valid MP3 file.")
        except Exception as e:
            print(f"Error adding metadata to {mp3_filename}: {e}")

        print(f"Downloaded {mp3_filename}\n")
        return

    def downloadNextSong(self, songIndex, songs, playlistTitle):
        if songIndex >= len(songs):
            return
        song = songs[songIndex]
        print(song)

        search = Search(f"{song[0]} {song[1]} {song[2]}")
        if not search.results:
            print(f"No se encontraron resultados para '{song[0]} {song[1]} {song[2]}'. Omitiendo canción.")
            self.downloadNextSong(songIndex + 1, songs, playlistTitle)
            return

        playlistFolder = self.createFolder(playlistTitle)
        self.downloadSong(songIndex + 1, song[0], song[1], song[3], song[2], song[4], song[5], song[6], song[7], song[8], search.results[0].watch_url, playlistFolder)

        self.downloadNextSong(songIndex + 1, songs, playlistTitle)

    def validateUrl(self, url):
        url_pattern = re.compile(r'https://open.spotify.com/playlist/[a-zA-Z0-9]+')

        if not url_pattern.match(url):
            print(f"ERROR INVALID URL\n")
            return False

        playlistID = self.getPlaylistID(url)
        try:
            playlist = self.spotify.playlist(playlistID)
        except spotipy.client.SpotifyException:
            print('f"ERROR INVALID PLAYLIST\n"')
            return False
        return True

    def downloadPlaylist(self):
        link = self.url_input.text()
        if self.validateUrl(link):
            playlistID = self.getPlaylistID(link)
            playlistData = self.spotify.playlist(playlistID)
            playlistName = self.getPlaylistTitle(playlistData)
            songs = self.getPlaylistTracks(link)
            self.downloadNextSong(0, songs, playlistName)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    downloader = SpotifyPlaylistDownloader()
    downloader.show()
    sys.exit(app.exec())