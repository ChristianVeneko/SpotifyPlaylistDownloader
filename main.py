import spotipy
import os
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from pytube import Search

# Crear Variables de Youtube y Search de youtube
yt = YouTube
s = Search

# Crear un objeto de autenticación con el ID del cliente y el secreto del cliente
auth_manager = SpotifyClientCredentials(client_id='d67481b0a3134e21a4870f42f4988bf3', client_secret='a3bd5765d10a4b66991097d607e4cde9')

# Crear un objeto de la API de Spotify con el objeto de autenticación
spotify = spotipy.Spotify(auth_manager=auth_manager)

# Definir el enlace de la playlist
link = 'https://open.spotify.com/playlist/7mRg9eazDDFtr3TVaBpVtD'

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
    

for song in songs:
    search = s(song[0] + ' - ' + song[1])
    # print('Title')
    # print(search.results[0].title)
    # print('Link')
    # print(search.results[0].watch_url)
    
    playlistFolder = createFolder(playlistTitle)

print(playlistFolder)