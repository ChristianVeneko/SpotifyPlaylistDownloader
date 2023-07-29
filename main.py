import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from pytube import YouTube
from pytube import Search

# Crear Variables de Youtube y Search de youtube
yt = YouTube
s = Search
class SpotifyPlaylisDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Descargador de YouTube")
        
        # Cargar el logo
        self.logo = tk.PhotoImage(file="logo.png")
        self.logo = self.logo.subsample(10)

        
        # Crear los widgets de la interfaz
        self.logo_label = tk.Label(master, image=self.logo)
        self.title_label = tk.Label(master, text="Descargador de YouTube", font=("Arial", 24))
        self.url_label = tk.Label(master, text="URL del video:")
        self.url_entry = tk.Entry(master, width=50)
        self.download_button = tk.Button(master, text="Descargar", command=self.main)
        self.progress_label = tk.Label(master, text="Progreso:")
        self.progress_text = tk.Text(master, height=10, width=50)
        
        # Ubicar los widgets en la interfaz
        self.logo_label.grid(row=0, column=0, columnspan=2, pady=10)
        self.title_label.grid(row=1, column=0, columnspan=2, pady=10)
        self.url_label.grid(row=2, column=0, pady=10)
        self.url_entry.grid(row=2, column=1, pady=10)
        self.download_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.progress_label.grid(row=4, column=0, pady=10)
        self.progress_text.grid(row=5, column=0, columnspan=2, pady=10)
        
    def main(self):
        # Crear un objeto de autenticación con el ID del cliente y el secreto del cliente
        auth_manager = SpotifyClientCredentials(client_id='d67481b0a3134e21a4870f42f4988bf3', client_secret='a3bd5765d10a4b66991097d607e4cde9')
        # Crear un objeto de la API de Spotify con el objeto de autenticación
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        # Definir el enlace de la playlist
        link = self.url_entry.get()

        # Extraer el ID de la playlist del enlace
        playlist_id = link.split('/')[-1]

        # Crear una lista vacía para almacenar las canciones
        songs = []
        
        # Inicializar el offset y el límite
        offset = 0
        limit = 50

        # Obtener el número total de elementos de la playlist
        total = spotify.playlist_items(playlist_id, limit=1)['total']

        # Obtener el titulo de la playlist
        playlist_data = spotify.playlist(playlist_id)
        playlistTitle = playlist_data["name"]
        # Recorrer los elementos de la playlist por lotes de 50
        while offset < total:
        # Obtener los elementos de la playlist con el offset y el límite actuales
            results = spotify.playlist_items(playlist_id, offset=offset, limit=limit)
            # Recorrer los resultados y extraer los datos relevantes
            for item in results['items']:
                song_name = item['track']['name']
                artist_name = item['track']['artists'][0]['name']   
                songs.append((song_name, artist_name))
            offset += limit

        # Funcion para crear las carpetas de las canciones
        def createFolder(title):
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

        def downloadSong(songTitle, videoUrl, folderRoute):
            youtube = YouTube(videoUrl)

            streams = youtube.streams.filter(only_audio=True)
            streams_with_abr = [(s, int(s.abr[:-4])) for s in streams if s.abr]
            streams_sorted = sorted(streams_with_abr, key=lambda s: s[1])
            stream = streams_sorted[-1][0]

            ruta_descarga = r"{}".format(folderRoute)
            if not os.path.exists(ruta_descarga):
                os.makedirs(ruta_descarga)
            
            outSong = stream.download(output_path=ruta_descarga)
            base, ext = os.path.splitext(outSong)
            song = base + '.mp3'
            os.rename(outSong, song) 
            return

        for song in songs:
            search = s(song[0] + ' - ' + song[1])

            playlistFolder = createFolder(playlistTitle)
            self.progress_text.insert(tk.END, f"Downloading {search.results[0].title}\n")
            downloadSong(search.results[0].title,search.results[0].watch_url, playlistFolder)
            self.progress_text.insert(tk.END, f"Download finished of  {search.results[0].title}\n")
        self.progress_text.insert(tk.END, f"Playlist download succefully finished\n")
root = tk.Tk()
app = SpotifyPlaylisDownloader(root)
root.mainloop()