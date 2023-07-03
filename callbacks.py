from typing import Any

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, no_update, ALL, ctx, State
from dash.exceptions import PreventUpdate
from spotipy import Spotify, SpotifyException, SpotifyPKCE, SpotifyOauthError

from layout import TrackTile

SPOTIFY_URI_START = 'https://open.spotify.com/'
TRACK_IDENTIFIER = '/track/'
ALBUM_IDENTIFIER = '/album/'
PLAYLIST_IDENTIFIER = '/playlist/'
PARAMETER_IDENTIFIER = '?'
MAX_TRACK_REQ_NO = 50
MAX_FEATURE_REQ_NO = 100
DEFAULT_DOUBLE_SMALLER = 50
DEFAULT_HALF_GREATER = 130


def is_spotify_uri(uri: str) -> bool:
    return uri.startswith(SPOTIFY_URI_START)


def is_album_uri(uri: str) -> bool:
    return ALBUM_IDENTIFIER in uri


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


def parse_album_uri(uri: str):
    start = uri.index(ALBUM_IDENTIFIER)
    if PARAMETER_IDENTIFIER in uri:
        end = uri.index(PARAMETER_IDENTIFIER)
    else:
        end = len(uri)
    return uri[start + len(ALBUM_IDENTIFIER):end]


def parse_playlist_uri(uri: str):
    start = uri.index(PLAYLIST_IDENTIFIER)
    if PARAMETER_IDENTIFIER in uri:
        end = uri.index(PARAMETER_IDENTIFIER)
    else:
        end = len(uri)
    return uri[start + len(PLAYLIST_IDENTIFIER):end]


def get_content(spotify: Spotify, track_id: str) -> dict:
    track = get_tracks(spotify, [track_id])[0]
    features = get_features(spotify, [track_id])[0]

    track_data = dict()
    track_data['title'] = track['name']
    track_data['artist'] = ', '.join(artist['name'] for artist in track['artists'])
    track_data['img_url'] = choose_image_url(track['album']['images'], 50)
    track_data['track_id'] = track['uri']
    track_data['tempo'] = features['tempo']

    return track_data


def get_contents(spotify: Spotify, tracks: list[dict]) -> list[dict]:
    if not tracks:
        return list()

    features = get_features(spotify, [track['id'] for track in tracks])

    result = list()
    for idx in range(len(tracks)):
        track_data = dict()

        track = tracks[idx]

        track_data['title'] = track['name']
        track_data['artist'] = ', '.join(artist['name'] for artist in track['artists'])
        track_data['img_url'] = choose_image_url(track['album']['images'], 50)
        track_data['track_id'] = track['uri']
        track_data['tempo'] = features[idx]['tempo']

        result.append(track_data)

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


def get_playlist_tracks(spotify: Spotify, playlist_id: str) -> list[dict]:
    offset = 0
    tracks = list()
    while True:
        items_info = spotify.playlist_items(playlist_id, offset=offset)
        tracks.extend(item['track'] for item in items_info['items'])
        if items_info['next'] is None:
            break
        offset = items_info['offset'] + len(items_info['items'])
    return tracks


def get_album_tracks(spotify: Spotify, album_id: str) -> list[dict]:
    offset = 0
    tracks = list()
    while True:
        items_info = spotify.album_tracks(album_id, offset=offset)
        tracks.extend(items_info['items'])
        if items_info['next'] is None:
            break
        offset = items_info['offset'] + len(items_info['items'])
    return tracks


def choose_image_url(images: list[dict], min_height: int) -> str:
    current_url = ''
    for image in images:
        if image['height'] < min_height:
            return current_url
        current_url = image['url']
    return current_url


def filter_tempo(filter_settings: dict[str, float], tempo) -> bool:
    if filter_settings:
        if 'greater' in filter_settings and tempo < filter_settings['greater']:
            return False
        if 'smaller' in filter_settings and tempo > filter_settings['smaller']:
            return False
    return True


def correct_tempo(double_smaller: float, half_greater: float, tempo) -> Any:
    if tempo < double_smaller:
        return tempo * 2
    if tempo > half_greater:
        return tempo / 2
    return tempo


def callbacks(app: Dash, spotify: Spotify, auth_manager: SpotifyPKCE):
    @app.callback(
        Output('content-storage', 'data'),
        Output('url-input', 'value'),
        Output('error-bar', 'is_open', allow_duplicate=True),
        Output('error-bar', 'children', allow_duplicate=True),
        Input('url-input', 'value')
    )
    def update_content_storage(uri: str):
        if not uri:
            raise PreventUpdate

        if not is_spotify_uri(uri):
            return no_update, '', True, 'No Spotify URL.'

        if is_track_uri(uri):
            track_id = parse_track_uri(uri)
            try:
                content = get_content(spotify, track_id)
                return [content], '', False, no_update
            except SpotifyException as e:
                return no_update, '', True, e.msg
        elif is_album_uri(uri):
            album_id = parse_album_uri(uri)
            try:
                album_tracks = get_album_tracks(spotify, album_id)
                contents = get_contents(spotify, album_tracks)
                return contents, '', False, dash.no_update
            except SpotifyException as e:
                return no_update, '', True, e.msg
        elif is_playlist_uri(uri):
            playlist_id = parse_playlist_uri(uri)
            try:
                playlist_tracks = get_playlist_tracks(spotify, playlist_id)
                contents = get_contents(spotify, playlist_tracks)
                return contents, '', False, dash.no_update
            except SpotifyException as e:
                return no_update, '', True, e.msg

        return no_update, '', True, 'This kind of URL is not supported.'

    @app.callback(
        Output('tracks', 'children'),
        Input('content-storage', 'modified_timestamp'),
        Input('filter-settings', 'modified_timestamp'),
        State('content-storage', 'data'),
        State('filter-settings', 'data')
    )
    def update_content(_0, _1, data: list[dict], filter_settings: dict[str, float]):
        if not data:
            raise PreventUpdate

        double_smaller = DEFAULT_DOUBLE_SMALLER
        half_greater = DEFAULT_HALF_GREATER
        if filter_settings:
            if 'double' in filter_settings:
                double_smaller = filter_settings['double']
            if 'half' in filter_settings:
                half_greater = filter_settings['half']

        return [
            TrackTile(
                track_data['title'],
                track_data['artist'],
                track_data['img_url'],
                track_data['track_id'],
                correct_tempo(double_smaller, half_greater, track_data['tempo'])
            )
            for track_data in data
            if filter_tempo(filter_settings, track_data['tempo'])
        ]

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
        Output('to-queue-done-storage', 'data'),
        Output('error-bar', 'is_open', allow_duplicate=True),
        Output('error-bar', 'children', allow_duplicate=True),
        Input({'type': 'to-queue', 'id': ALL}, 'n_clicks'),
        State('to-queue-done-storage', 'data'),
        prevent_initial_call=True
    )
    def add_to_queue(n_clicks, to_queue_done_data: list):
        if all(n is None for n in n_clicks):
            raise PreventUpdate

        _id = ctx.triggered_id
        track_id = _id['id']
        if not track_id:
            raise PreventUpdate

        try:
            spotify.add_to_queue(track_id)
        except SpotifyException as e:
            return no_update, True, e.msg

        if not to_queue_done_data:
            to_queue_done_data = list()
        if track_id not in to_queue_done_data:
            to_queue_done_data.append(track_id)
        return to_queue_done_data, no_update, no_update

    @app.callback(
        Output({'type': 'to-queue-done', 'id': ALL}, 'is_open'),
        Input('to-queue-done-storage', 'modified_timestamp'),
        State({'type': 'to-queue', 'id': ALL}, 'id'),
        State('to-queue-done-storage', 'data')
    )
    def update_to_queue_done(_, ids, to_queue_done_data):
        if not to_queue_done_data:
            raise PreventUpdate

        return [
            _id['id'] in to_queue_done_data
            for _id in ids
        ]

    @app.callback(
        Output('filter-modal', 'is_open'),
        Input('filter', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_filter(_):
        return True

    @app.callback(
        Output('filter-greater-input', 'disabled'),
        Input('check-filter-greater', 'value')
    )
    def enable_filter_greater_input(check):
        return not check

    @app.callback(
        Output('filter-smaller-input', 'disabled'),
        Input('check-filter-smaller', 'value')
    )
    def enable_filter_smaller_input(check):
        return not check

    @app.callback(
        Output('filter-greater-input', 'invalid'),
        Input('filter-greater-input', 'value'),
        Input('check-filter-greater', 'value')
    )
    def validate_filter_greater_input(value_input, check):
        if not check:
            return False
        return not (value_input and str(value_input).isnumeric() and float(value_input) >= 0)

    @app.callback(
        Output('filter-smaller-input', 'invalid'),
        Input('filter-smaller-input', 'value'),
        Input('check-filter-smaller', 'value')
    )
    def validate_filter_smaller_input(value_input, check):
        if not check:
            return False
        return not (value_input and str(value_input).isnumeric() and float(value_input) >= 0)

    @app.callback(
        Output('double-smaller-input', 'invalid'),
        Input('double-smaller-input', 'value')
    )
    def validate_double_smaller_input(value_input):
        return not (value_input and str(value_input).isnumeric() and float(value_input) >= 0)

    @app.callback(
        Output('half-greater-input', 'invalid'),
        Input('half-greater-input', 'value')
    )
    def validate_half_greater_input(value_input):
        return not (value_input and str(value_input).isnumeric() and float(value_input) >= 0)

    @app.callback(
        Output('filter-settings', 'data'),
        Input('filter-modal', 'is_open'),
        State('check-filter-greater', 'value'),
        State('check-filter-smaller', 'value'),
        State('filter-greater-input', 'value'),
        State('filter-smaller-input', 'value'),
        State('double-smaller-input', 'value'),
        State('half-greater-input', 'value'),
        prevent_initial_call=True
    )
    def update_filter_settings(is_open, check_greater, check_smaller, greater_input, smaller_input, double_input, half_input):
        if is_open:
            raise PreventUpdate

        filter_settings = dict()
        if check_greater:
            if not (greater_input and str(greater_input).isnumeric()):
                raise PreventUpdate
            filter_settings['greater'] = float(greater_input)
        if check_smaller:
            if not (smaller_input and str(smaller_input).isnumeric()):
                raise PreventUpdate
            filter_settings['smaller'] = float(smaller_input)

        if not (double_input and str(double_input).isnumeric()):
            raise PreventUpdate
        filter_settings['double'] = float(double_input)
        if not (half_input and str(half_input).isnumeric()):
            raise PreventUpdate
        filter_settings['half'] = float(half_input)

        return filter_settings

    @app.callback(
        Output('check-filter-greater', 'value'),
        Output('check-filter-smaller', 'value'),
        Output('filter-greater-input', 'value'),
        Output('filter-smaller-input', 'value'),
        Output('double-smaller-input', 'value'),
        Output('half-greater-input', 'value'),
        Input('filter-modal', 'is_open'),
        State('filter-settings', 'data')
    )
    def read_filter_settings(is_open, filter_settings: dict[str, float]):
        if not is_open:
            raise PreventUpdate

        if not filter_settings:
            return no_update, no_update, no_update, no_update, DEFAULT_DOUBLE_SMALLER, DEFAULT_HALF_GREATER

        check_greater = False
        check_smaller = False
        greater_input = None
        smaller_input = None

        if 'greater' in filter_settings:
            check_greater = True
            greater_input = filter_settings['greater']
        if 'smaller' in filter_settings:
            check_smaller = True
            smaller_input = filter_settings['smaller']
        if 'double' in filter_settings:
            double_input = filter_settings['double']
        else:
            double_input = DEFAULT_DOUBLE_SMALLER
        if 'half' in filter_settings:
            half_input = filter_settings['half']
        else:
            half_input = DEFAULT_HALF_GREATER

        return check_greater, check_smaller, greater_input, smaller_input, double_input, half_input
