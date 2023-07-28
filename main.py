import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Crear un objeto de autenticación con el ID del cliente y el secreto del cliente
auth_manager = SpotifyClientCredentials(client_id='tu_id_de_cliente', client_secret='tu_secreto_de_cliente')

# Crear un objeto de la API de Spotify con el objeto de autenticación
spotify = spotipy.Spotify(auth_manager=auth_manager)

