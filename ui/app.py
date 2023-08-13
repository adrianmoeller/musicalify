import dash_bootstrap_components as dbc
import spotipy
from dash import Dash, html
from dash_extensions.enrich import DashProxy
from spotipy import Spotify, SpotifyPKCE

from ui.callbacks import callbacks
from ui.layout.layout import Layout

APP_NAME = 'Musicalify'


class App:
    debug: bool
    app: Dash
    auth_manager: SpotifyPKCE
    spotify: Spotify

    def __init__(self, debug: bool):
        self.debug = debug
        self.app = DashProxy(
            __name__,
            external_stylesheets=[dbc.icons.BOOTSTRAP, dbc.themes.DARKLY],
        )
        self.app.title = APP_NAME
        self.app.layout = html.Div([Layout()])

        self.auth_manager = SpotifyPKCE(
            scope='user-modify-playback-state,playlist-read-private'
        )
        self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)

        callbacks(self.app, self.spotify, self.auth_manager)

    def run(self):
        self.app.run_server(debug=self.debug)
