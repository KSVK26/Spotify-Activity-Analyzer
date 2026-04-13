import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI


def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-read-recently-played user-top-read user-read-private user-read-email",
        open_browser=False,
    )


def get_auth_url():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return auth_url


def get_token_from_code(code: str):
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)
    return token_info


def get_spotify_client(access_token: str):
    return spotipy.Spotify(auth=access_token)
