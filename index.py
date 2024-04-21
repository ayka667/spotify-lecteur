import json
import tkinter as tk
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser

# Charger les informations de configuration depuis le fichier config.json
def load_config():
    try:
        with open("config.json") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        tk.messagebox.showerror("Erreur", "Le fichier de configuration config.json est introuvable.")
        return None

# Fenêtre pour la connexion Spotify
def open_spotify_auth_window():
    global auth_window
    auth_window = tk.Toplevel(app)
    auth_window.title("Connexion à Spotify")

    auth_label = ttk.Label(auth_window, text="Connectez-vous à votre compte Spotify")
    auth_label.pack(pady=10)

    auth_button = ttk.Button(auth_window, text="Se connecter à Spotify", command=open_spotify_auth_url)
    auth_button.pack(pady=10)

# Fonction pour ouvrir le lien de connexion Spotify
def open_spotify_auth_url():
    auth_manager = SpotifyOAuth(client_id=config["SPOTIPY_CLIENT_ID"],
                                client_secret=config["SPOTIPY_CLIENT_SECRET"],
                                redirect_uri=config["SPOTIPY_REDIRECT_URI"],
                                scope="user-library-read streaming")
    auth_url = auth_manager.get_authorize_url()
    webbrowser.open(auth_url)

# Fonction pour récupérer l'access token après la connexion
def get_access_token(url):
    code = spotipy.util.parse_response_code(url)
    if code:
        auth_manager = SpotifyOAuth(client_id=config["SPOTIPY_CLIENT_ID"],
                                    client_secret=config["SPOTIPY_CLIENT_SECRET"],
                                    redirect_uri=config["SPOTIPY_REDIRECT_URI"],
                                    scope="user-library-read streaming")
        auth_manager.get_access_token(code)
        access_token = auth_manager.get_access_token(code)
        spotify = spotipy.Spotify(auth=access_token)
        devices = spotify.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            tk.messagebox.showinfo("Succès", "Connexion à Spotify réussie!")
            auth_window.destroy()
            show_main_window()
        else:
            tk.messagebox.showerror("Erreur", "Aucun appareil trouvé pour la lecture.")
    else:
        tk.messagebox.showerror("Erreur", "Impossible de récupérer l'access token.")

# Afficher la fenêtre principale
def show_main_window():
    global main_window
    main_window = tk.Toplevel(app)
    main_window.title("Spotify Music Streamer")

    main_frame = ttk.Frame(main_window, padding="20")
    main_frame.grid(row=0, column=0)

    song_label = ttk.Label(main_frame, text="Entrez le lien de la chanson Spotify:")
    song_label.grid(row=0, column=0, sticky="w")

    global song_entry
    song_entry = ttk.Entry(main_frame, width=40)
    song_entry.grid(row=0, column=1)

    play_button = ttk.Button(main_frame, text="Jouer", command=play_music)
    play_button.grid(row=1, column=1, pady=10)

# Fonction pour lire la musique en boucle
def play_music():
    selected_song = song_entry.get()
    if not selected_song:
        tk.messagebox.showerror("Erreur", "Veuillez saisir un lien Spotify valide!")
        return

    spotify = spotipy.Spotify(auth=access_token)
    track_id = selected_song.split('/')[-1]
    try:
        spotify.start_playback(uris=[f"spotify:track:{track_id}"], device_id=device_id, context_uri=None, offset=None)
    except Exception as e:
        tk.messagebox.showerror("Erreur", f"Erreur de lecture: {str(e)}")

# Chargement de la configuration
config = load_config()

if config:
    # Création de l'application Tkinter
    app = tk.Tk()
    app.title("Spotify Music Streamer")

    open_spotify_auth_window()

    # Récupération de l'access token après la connexion
    access_token = None
    device_id = None
    auth_window.after(100, lambda: get_access_token(auth_window.clipboard_get()))

    app.mainloop()
