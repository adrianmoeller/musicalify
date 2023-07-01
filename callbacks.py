import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, no_update, ALL, ctx, State
from dash.exceptions import PreventUpdate
from spotipy import Spotify, SpotifyException, SpotifyPKCE, SpotifyOauthError

from layout import TrackTile

SPOTIFY_URI_START = 'https://open.spotify.com/'
TRACK_IDENTIFIER = '/track/'
PLAYLIST_IDENTIFIER = '/playlist/'
PARAMETER_IDENTIFIER = '?'
MAX_TRACK_REQ_NO = 50
MAX_FEATURE_REQ_NO = 100


def is_spotify_uri(uri: str) -> bool:
    return uri.startswith(SPOTIFY_URI_START)


def is_track_uri(uri: str) -> bool:
    return TRACK_IDENTIFIER in uri


def is_playlist_uri(uri: str) -> bool:
    return PLAYLIST_IDENTIFIER in uri


def parse_track_uri(uri: str):
    start = uri.index(TRACK_IDENTIFIER)
    if PARAMETER_IDENTIFIER in uri:
        end = uri.index(PARAMETER_IDENTIFIER)
    else:
        end = len(uri)
    return uri[start + len(TRACK_IDENTIFIER):end]


def parse_playlist_uri(uri: str):
    start = uri.index(PLAYLIST_IDENTIFIER)
    if PARAMETER_IDENTIFIER in uri:
        end = uri.index(PARAMETER_IDENTIFIER)
    else:
        end = len(uri)
    return uri[start + len(PLAYLIST_IDENTIFIER):end]


def get_contents_and_create_tiles(spotify: Spotify, track_ids: list[str]) -> list[TrackTile]:
    if not track_ids:
        return list()

    tracks = get_tracks(spotify, track_ids)
    features = get_features(spotify, track_ids)

    result = list()
    for idx in range(len(track_ids)):
        track = tracks[idx]

        title = track['name']
        artist = ', '.join(artist['name'] for artist in track['artists'])
        img_url = choose_image_url(track['album']['images'], 50)
        track_id = track['uri']
        tempo = features[idx]['tempo']
        if tempo > 130:
            tempo = tempo / 2

        result.append(TrackTile(idx, title, artist, img_url, track_id, tempo))

    return result


def get_tracks(spotify: Spotify, track_ids: list[str]):
    num_of_full_requests = int(len(track_ids) / MAX_TRACK_REQ_NO)

    result = list()
    for idx in range(num_of_full_requests):
        tracks = spotify.tracks(track_ids[idx * MAX_TRACK_REQ_NO:(idx + 1) * MAX_TRACK_REQ_NO])
        result.extend(tracks['tracks'])
    missing_track_ids = track_ids[num_of_full_requests * MAX_TRACK_REQ_NO:]
    if missing_track_ids:
        tracks = spotify.tracks(missing_track_ids)
        result.extend(tracks['tracks'])

    return result


def get_features(spotify: Spotify, track_ids: list[str]):
    num_of_full_requests = int(len(track_ids) / MAX_FEATURE_REQ_NO)

    result = list()
    for idx in range(num_of_full_requests):
        features = spotify.audio_features(track_ids[idx * MAX_FEATURE_REQ_NO:(idx + 1) * MAX_FEATURE_REQ_NO])
        result.extend(features)
    missing_track_ids = track_ids[num_of_full_requests * MAX_FEATURE_REQ_NO:]
    if missing_track_ids:
        features = spotify.audio_features(missing_track_ids)
        result.extend(features)

    return result


def choose_image_url(images: list[dict], min_height: int) -> str:
    current_url = ''
    for image in images:
        if image['height'] < min_height:
            return current_url
        current_url = image['url']
    return current_url


def callbacks(app: Dash, spotify: Spotify, auth_manager: SpotifyPKCE):
    @app.callback(
        Output('tracks', 'children'),
        Output('url-input', 'value'),
        Output('error-bar', 'is_open', allow_duplicate=True),
        Output('error-bar', 'children', allow_duplicate=True),
        Input('url-input', 'value')
    )
    def update_content(uri: str):
        if not uri:
            raise PreventUpdate

        if not is_spotify_uri(uri):
            return no_update, '', True, 'No Spotify URL.'

        if is_track_uri(uri):
            track_id = parse_track_uri(uri)
            try:
                track_tiles = get_contents_and_create_tiles(spotify, [track_id])
                return track_tiles, '', False, no_update
            except SpotifyException as e:
                return no_update, '', True, e.msg
        elif is_playlist_uri(uri):
            playlist_id = parse_playlist_uri(uri)
            try:
                items = spotify.playlist_items(playlist_id)['items']
                track_ids = [item['track']['id'] for item in items]
                track_tiles = get_contents_and_create_tiles(spotify, track_ids)
                return track_tiles, '', False, dash.no_update
            except SpotifyException as e:
                return no_update, '', True, e.msg

        return no_update, '', True, 'This kind of URL is not supported.'

    @app.callback(
        Output('user-header', 'children'),
        Input('url', 'href')
    )
    def init_authentication(url: str):
        if not url:
            raise PreventUpdate

        access_token = ""

        token_info = auth_manager.get_cached_token()
        if token_info:
            access_token = token_info['access_token']
        else:
            code = auth_manager.parse_response_code(url)
            if code != url:
                try:
                    access_token = auth_manager.get_access_token(code)
                except SpotifyOauthError:
                    pass

        if access_token:
            user = spotify.current_user()
            return [html.I(className='bi bi-person-circle me-2'), html.Div(user['display_name'])]
        else:
            return [dbc.Button('Log in', id='log-in', href=auth_manager.get_authorize_url(), className='bg-secondary')]

    @app.callback(
        Output({'type': 'to-queue-done', 'id': ALL}, 'is_open'),
        Output('error-bar', 'is_open', allow_duplicate=True),
        Output('error-bar', 'children', allow_duplicate=True),
        Input({'type': 'to-queue', 'id': ALL, 'index': ALL}, 'n_clicks'),
        State({'type': 'to-queue-done', 'id': ALL}, 'is_open'),
        prevent_initial_call=True
    )
    def add_to_queue(n_clicks, is_done):
        if all(n is None for n in n_clicks):
            raise PreventUpdate

        _id = ctx.triggered_id
        track_id = _id['id']
        if not track_id:
            raise PreventUpdate

        try:
            spotify.add_to_queue(track_id)
        except SpotifyException as e:
            return is_done, True, e.msg

        is_done[_id['index']] = True
        return is_done, no_update, no_update
