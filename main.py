import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search
import shutil
import threading
import slugify
import re

# Crear Variables de Youtube y Search de youtube
yt = YouTube
s = Search

class SpotifyPlaylistDownloader:
    def __init__(self):
        self.initSpotify()
    
    def initSpotify(self):
        """Inicializa la conexión con la API de Spotify"""
        self.auth_manager = SpotifyClientCredentials(client_id='d67481b0a3134e21a4870f42f4988bf3',
                                                     client_secret='a3bd5765d10a4b66991097d607e4cde9')
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
    
    def getPlaylistTracks(self, playlistUrl):
        playlistID = self.getPlaylistID(playlistUrl)
        # Crear una lista vacía para almacenar las canciones
        tracks = []
        
        # Inicializar el offset y el límite
        offset = 0
        limit = 50
        # Obtener el número total de elementos de la playlist
        total = self.spotify.playlist_items(playlistID, limit=1)['total']
        # Recorrer los elementos de la playlist por lotes de 50
        while offset < total:
            results = self.spotify.playlist_items(playlistID, offset=offset, limit = limit)
            tracks.extend(self.extrackTracks(results['items']))
            offset += limit
            
        return tracks
            
    
    def getPlaylistTitle(self, data):
        return data["name"]
    
    def getPlaylistID(self, url):
        # Extraer el ID de la playlist del enlace
        return url.split('/')[-1]
    
    def extrackTracks(self, items):
        tracks = []
        # Recorrer los resultados y extraer los datos relevantes
        for item in items:
            track = item['track']
            name = track['name']
            artist = track['artists'][0]['name']
            tracks.append((name, artist))
        return tracks
        
    def createFolder(self, title):
        rutaActual = os.getcwd()

        # Nombre de la carpeta que quieres crear
        downloadFolder = "Downloads"

        # Ruta completa de la carpeta que quieres crear
        rutaDownloadFolder = os.path.join(rutaActual, downloadFolder)
        
        # Crear la carpeta si no existe
        if not os.path.exists(rutaDownloadFolder):
            os.mkdir(rutaDownloadFolder)

        playlistFolder = title

        # Ruta completa de la subcarpeta que quieres crear
        rutaPlaylistFolder = os.path.join(rutaDownloadFolder, playlistFolder)

        # Crear la subcarpeta si no existe
        if not os.path.exists(rutaPlaylistFolder):
            os.mkdir(rutaPlaylistFolder)
    
        return rutaPlaylistFolder
    
    def downloadSong(self, title, songArtist, videoUrl, folderRoute):
        youtube = YouTube(videoUrl)
        songTitle = title + ' - ' + songArtist
        streams = youtube.streams.filter(only_audio=True)
        streams_with_abr = [(s, int(s.abr[:-4])) for s in streams if s.abr]
        streams_sorted = sorted(streams_with_abr, key=lambda s: s[1])
        stream = streams_sorted[-1][0]

        downloadRoute = folderRoute
        if not os.path.exists(downloadRoute):
            os.makedirs(downloadRoute)
        
        mp3_filenameStr = str(songTitle)
        mp3_filename = slugify.slugify(mp3_filenameStr)  + '.mp3'
        print(f"Downloading {mp3_filename} ... \n")
        mp3_path = os.path.join(downloadRoute, mp3_filename)
    
        if os.path.exists(mp3_path):
            print(f"{mp3_filename} already exists. Skipping download.\n")
            return

        outSong = stream.download(output_path=downloadRoute)
        base, ext = os.path.splitext(outSong)
        songName = str(base) 
        song = slugify.slugify(songName)+ '.mp3'
        os.rename(outSong, song)
        os.rename(song, mp3_filename)
        shutil.move(mp3_filename, downloadRoute)

        print(f"Downloaded {mp3_filename}\n")
        return
    
    def downloadNextSong(self, songIndex, songs, playlistTitle):
        if songIndex >= len(songs):
            return
        song = songs[songIndex]
        print(song)
        
        search = s(song[0] + ' ' + song[1])
        playlistFolder = self.createFolder(playlistTitle)
        # Start the download process for the current song
        self.downloadSong(song[0], song[1], search.results[0].watch_url, playlistFolder)

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
    def main(self):
        # Definir el enlace de la playlist
        print
        link = input() 
        if(self.validateUrl(link) == True):
            playlistID = self.getPlaylistID(link)
            playlistData = self.spotify.playlist(playlistID)
            playlistName = self.getPlaylistTitle(playlistData)
            songs = self.getPlaylistTracks(link)
            
            self.downloadNextSong(0, songs, playlistName)
                

app = SpotifyPlaylistDownloader()
app.main()