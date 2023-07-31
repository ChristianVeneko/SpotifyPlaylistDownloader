import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
import customtkinter as ctk
from pytube import YouTube
from pytube import Search
from PIL import Image, ImageTk
import shutil
import threading

# Crear Variables de Youtube y Search de youtube
yt = YouTube
s = Search

class SpotifyPlaylistDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Spotify Playlist Downloader")
        self.frame = ctk.CTkFrame(master)
        
        # Cargar el logo
        light_logo = Image.open("Logo.png") 
        dark_logo = Image.open("logo.png")
        self.logo = ctk.CTkImage(light_image=light_logo, dark_image=dark_logo, size=(150, 150))

        # Crear los widgets de la interfaz
        self.logo_label = ctk.CTkLabel(master, image=self.logo)
        self.title_label = ctk.CTkLabel(master, text="Spotify Playlist Downloader", font=("Arial", 24))
        self.url_label = ctk.CTkLabel(master=root,
                     text="Playlist URL:",
                     text_color="#fff",
                     width=30,
                     font=("Helvetica", 24))
        self.url_entry = ctk.CTkEntry(master, width=300)
        self.download_button = ctk.CTkButton(master, text="Download", command=self.main, width=250, height= 50, font=('Arial',18))
        self.progress_label = ctk.CTkLabel(master=root,
                     text="Progress:",
                     text_color="#fff",
                     width=30,
                     font=("Helvetica", 24))
        self.progress_text = ctk.CTkTextbox(master, height=200, width=400)
        # self.progress_text.configure(state="disabled")
        
        self.logo_label.grid(row=0, column=0) 
        self.frame.grid(row=0, column=0) 
        self.title_label.grid(row=0, column=1) 
        self.url_label.grid(row=2, column=0, pady=10)
        self.url_entry.grid(row=2, column=1, pady=10)
        self.download_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.progress_label.grid(row=4, column=0, pady=10)
        self.progress_text.grid(row=5, column=0, columnspan=2, pady=10)

        # Configurar el peso de las columnas y las filas
        self.master.grid_columnconfigure(0, weight=1) 
        self.master.grid_columnconfigure(1, weight=2)
        self.master.grid_rowconfigure(0, weight=1) 
        self.master.grid_rowconfigure(5, weight=2) 
        
        # Inicializa los datos de la api de spotify
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

        mp3_filename = songTitle + '.mp3'
        self.progress_text.insert(ctk.END, f"Downloading {mp3_filename} ... \n")
        mp3_path = os.path.join(downloadRoute, mp3_filename)
    
        if os.path.exists(mp3_path):
            self.progress_text.insert(ctk.END, f"{mp3_filename} already exists. Skipping download.\n")
            return

        outSong = stream.download(output_path=downloadRoute)
        base, ext = os.path.splitext(outSong)
        song = base + '.mp3'
        os.rename(outSong, song)
        os.rename(song, mp3_filename)
        shutil.move(mp3_filename, downloadRoute)

        self.progress_text.insert(ctk.END, f"Downloaded {mp3_filename}\n")
        return
    
    def downloadNextSong(self, songIndex, songs, playlistTitle):
        if songIndex >= len(songs):
            return
        song = songs[songIndex]
        search = s(song[0] + ' - ' + song[1])
        playlistFolder = self.createFolder(playlistTitle)

        # Start the download process for the current song
        self.downloadSong(song[0], song[1], search.results[0].watch_url, playlistFolder)

        self.master.after(5000, self.downloadNextSong, songIndex + 1, songs, playlistTitle)
        
    
    def main(self):
        # Definir el enlace de la playlist
        link = self.url_entry.get() 
        playlistID = self.getPlaylistID(link)
        playlistData = self.spotify.playlist(playlistID)
        playlistName = self.getPlaylistTitle(playlistData)
        songs = self.getPlaylistTracks(link)
        self.master.after(1, self.downloadNextSong, 0, songs, playlistName) 
root = ctk.CTk()
app = SpotifyPlaylistDownloader(root)
root.mainloop()