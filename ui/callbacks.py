import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, html, no_update, ALL, ctx, State, MATCH
from dash.exceptions import PreventUpdate
from spotipy import Spotify, SpotifyException, SpotifyPKCE, SpotifyOauthError

import data.spotify_content_extraction as content_extr
import data.spotify_uri_utils as uri_utils
from ui.layout.track_tile import TrackTile

DEFAULT_DOUBLE_SMALLER = 50
DEFAULT_HALF_GREATER = 130

TRACKS_PER_PAGE = 80

SORT_STATE_NONE = 'none'
SORT_STATE_ASC = 'ascending'
SORT_STATE_DESC = 'descending'


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

        if not uri_utils.is_spotify_uri(uri):
            return no_update, '', True, 'No Spotify URL.'

        try:
            if uri_utils.is_track_uri(uri):
                content = content_extr.get_content_track(spotify, uri_utils.parse_track_uri(uri))
            elif uri_utils.is_album_uri(uri):
                content = content_extr.get_content_album(spotify, uri_utils.parse_album_uri(uri))
            elif uri_utils.is_playlist_uri(uri):
                content = content_extr.get_content_playlist(spotify, uri_utils.parse_playlist_uri(uri))
            else:
                return no_update, '', True, 'This kind of URL is not supported.'
            return content, '', False, no_update
        except SpotifyException as e:
            return no_update, '', True, e.msg

    @app.callback(
        Output('content-title', 'children'),
        Output('tracks', 'children'),
        Output('pager', 'max_value'),
        Output('pager', 'class_name'),
        Input('content-storage', 'modified_timestamp'),
        Input('filter-settings', 'modified_timestamp'),
        Input('bpm-sort-state', 'modified_timestamp'),
        Input('corrected-bpm-storage', 'modified_timestamp'),
        Input('pager', 'active_page'),
        State('content-storage', 'data'),
        State('filter-settings', 'data'),
        State('bpm-sort-state', 'data'),
        State('corrected-bpm-storage', 'data')
    )
    def update_content(_0, _1, _2, _3, active_page, data: dict, filter_settings: dict[str, float], bpm_sort_state: str, corrected_bpm_data: dict[str, float]):
        if not data:
            raise PreventUpdate

        double_smaller = DEFAULT_DOUBLE_SMALLER
        half_greater = DEFAULT_HALF_GREATER
        if filter_settings:
            if 'double' in filter_settings:
                double_smaller = filter_settings['double']
            if 'half' in filter_settings:
                half_greater = filter_settings['half']

        if not corrected_bpm_data:
            corrected_bpm_data = dict()

        tracks_data = data['tracks']

        for track_data in tracks_data:
            if track_data['track_id'] in corrected_bpm_data:
                track_data['tempo'] = corrected_bpm_data[track_data['track_id']]
            track_data['tempo'] = content_extr.correct_tempo(double_smaller, half_greater, track_data['tempo'])

        filtered_data = [
            track_data
            for track_data in tracks_data
            if content_extr.filter_tempo(filter_settings, track_data['tempo'])
        ]

        if bpm_sort_state == SORT_STATE_ASC:
            filtered_data.sort(key=lambda d: d['tempo'])
        if bpm_sort_state == SORT_STATE_DESC:
            filtered_data.sort(key=lambda d: d['tempo'], reverse=True)

        if active_page is None:
            active_page = 1
        num_of_pages = int(len(filtered_data) / TRACKS_PER_PAGE) + 1
        if num_of_pages > 1:
            start_offset = (active_page - 1) * TRACKS_PER_PAGE
            end_offset = active_page * TRACKS_PER_PAGE
            if end_offset > len(filtered_data):
                end_offset = len(filtered_data)
            display_data = filtered_data[start_offset:end_offset]
        else:
            display_data = filtered_data

        tracks = [
            TrackTile(
                track_data['title'],
                track_data['artist'],
                track_data['img_url'],
                track_data['track_id'],
                track_data['tempo'],
                track_data['acousticness'],
                track_data['danceability'],
                track_data['energy'],
                track_data['instrumentalness'],
                track_data['valence']
            )
            for track_data in display_data
        ]

        title = html.Div(data['title'], className='p-1 mt-3 h3 fw-bold') if data['title'] else None

        return title, tracks, num_of_pages, 'm-1' if num_of_pages > 1 else 'd-none'

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
            return [
                html.I(className='bi bi-person-circle me-2'),
                html.Div(user['display_name'])
            ]
        else:
            return [dbc.Button(
                children='Log in',
                id='log-in',
                href=auth_manager.get_authorize_url(),
                className='bg-secondary',
                size='sm'
            )]

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

    @app.callback(
        Output('bpm-sort-state', 'data'),
        Input('sort', 'n_clicks'),
        State('bpm-sort-state', 'data'),
        prevent_initial_call=True
    )
    def update_bpm_sort_state(_, bpm_sort_state: str):
        if not bpm_sort_state or bpm_sort_state == SORT_STATE_NONE:
            return SORT_STATE_ASC
        if bpm_sort_state == SORT_STATE_ASC:
            return SORT_STATE_DESC
        if bpm_sort_state == SORT_STATE_DESC:
            return SORT_STATE_NONE

    @app.callback(
        Output('sort-icon', 'className'),
        Input('bpm-sort-state', 'modified_timestamp'),
        State('bpm-sort-state', 'data')
    )
    def update_bpm_sort_icon(_, bpm_sort_state):
        margin = ' me-1'
        if not bpm_sort_state or bpm_sort_state == SORT_STATE_NONE:
            return 'bi bi-arrow-down-up' + margin
        if bpm_sort_state == SORT_STATE_ASC:
            return 'bi bi-arrow-down' + margin
        if bpm_sort_state == SORT_STATE_DESC:
            return 'bi bi-arrow-up' + margin

    @app.callback(
        Output('local-settings-modal', 'is_open'),
        Input('local-settings', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_local_settings(_):
        return True

    @app.callback(
        Output('corrected-bpm-storage', 'clear_data'),
        Input('reset-corrected-bpm', 'n_clicks'),
        prevent_initial_call=True
    )
    def reset_corrected_bpm_values(_):
        return True

    @app.callback(
        Output('edit-bpm-value-modal', 'is_open', allow_duplicate=True),
        Output('edit-bpm-value-input', 'value'),
        Output('edit-bpm-value-track-id', 'children'),
        Output('error-bar', 'is_open', allow_duplicate=True),
        Output('error-bar', 'children', allow_duplicate=True),
        Input({'type': 'edit-bpm', 'id': ALL}, 'n_clicks'),
        State('corrected-bpm-storage', 'data'),
        prevent_initial_call=True
    )
    def open_edit_bpm_value(n_clicks, corrected_bpm_data: dict[str, float]):
        if all(n is None for n in n_clicks):
            raise PreventUpdate

        _id = ctx.triggered_id
        track_id = _id['id']
        if not track_id:
            raise PreventUpdate

        try:
            if corrected_bpm_data and track_id in corrected_bpm_data:
                tempo = corrected_bpm_data[track_id]
            else:
                track_data = content_extr.get_content_track(spotify, track_id)
                tempo = round(track_data['tracks'][0]['tempo'])
            return True, tempo, track_id, False, no_update
        except SpotifyException as e:
            return False, no_update, no_update, True, e.msg

    @app.callback(
        Output({'type': 'stats-popover', 'id': MATCH}, 'is_open'),
        Input({'type': 'edit-bpm', 'id': MATCH}, 'n_clicks'),
        prevent_initial_call=True
    )
    def close_popover_on_edit_click(_):
        return False

    @app.callback(
        Output('corrected-bpm-storage', 'data'),
        Output('edit-bpm-value-modal', 'is_open', allow_duplicate=True),
        Input('edit-bpm-value-save', 'n_clicks'),
        State('edit-bpm-value-input', 'value'),
        State('edit-bpm-value-track-id', 'children'),
        State('corrected-bpm-storage', 'data'),
        prevent_initial_call=True
    )
    def save_bpm_value(_, input_value, track_id, corrected_bpm_data: dict[str, float]):
        if not track_id:
            raise PreventUpdate

        if not corrected_bpm_data:
            corrected_bpm_data = dict()

        if not input_value:
            if track_id in corrected_bpm_data:
                corrected_bpm_data.pop(track_id)
                return corrected_bpm_data, False
            else:
                raise PreventUpdate

        try:
            input_value_float = float(input_value)
            corrected_bpm_data[track_id] = input_value_float
            return corrected_bpm_data, False
        except Exception:
            raise PreventUpdate
