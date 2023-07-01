import dash
import dash_bootstrap_components as dbc
from dash import html, dcc


class Layout(html.Div):
    def __init__(self):
        super().__init__(
            id='layout',
            children=[
                dcc.Location(id='url'),
                html.Div(
                    id='header',
                    children=[
                        html.Img(
                            src=dash.get_asset_url('logos/Spotify_Logo_RGB_White.png'),
                            width=120,
                            className='py-1'
                        ),
                        html.Div(
                            id='user-header',
                            children=[],
                            className='d-flex flex-row'
                        )
                    ],
                    className='header p-2 d-flex justify-content-between align-items-center'
                ),
                html.Div(
                    children=[
                        dbc.Input(
                            id='url-input',
                            type='url',
                            placeholder='Paste your track or playlist URL here.',
                            className='url-input w-100 p-4'
                        )
                    ],
                    className='p-1'
                ),
                html.Div(
                    id='content',
                    children=[
                        dbc.ListGroup(
                            id='tracks',
                            className='p-1'
                        ),
                        html.Div(
                            children=[
                                dbc.Button(
                                    children=[
                                        html.Img(
                                            src=dash.get_asset_url('logos/Spotify_Icon_RGB_White.png'),
                                            width=25,
                                            className='me-2'
                                        ),
                                        'OPEN SPOTIFY'
                                    ],
                                    href='spotify:',
                                    className='px-3 py-2 bg-secondary d-flex justify-content-center'
                                )
                            ],
                            className='p-2 d-flex justify-content-center'
                        )
                    ],
                    className='content'
                ),
                dbc.Toast(
                    id='error-bar',
                    header='Error',
                    icon='danger',
                    duration=10000,
                    dismissable=True,
                    style={"position": "fixed", "bottom": 20, "right": 20, "width": 350},
                    is_open=False
                )
            ],
            className='p-1'
        )


class TrackTile(dbc.ListGroupItem):
    def __init__(self,
                 index: int,
                 title: str,
                 artist: str,
                 img_url: str,
                 track_id: str,
                 tempo: float
                 ):
        super().__init__(
            children=[
                html.Div(
                    children=[
                        html.Img(src=img_url, width=50, height=50),
                        html.Div(
                            children=[
                                html.A(
                                    title,
                                    className='title fw-bold text-body text-decoration-none',
                                    href=track_id,
                                    target='_blank'
                                ),
                                html.Div(artist, className='text-muted')
                            ],
                            className='d-flex flex-column ms-3'
                        )
                    ],
                    className='d-flex flex-row'
                ),
                html.Div(
                    children=[
                        html.Div(f'{round(tempo)} bpm'),
                        html.Div(
                            children=[
                                html.A(
                                    html.I(className='bi bi-view-stacked'),
                                    id={'type': 'to-queue', 'id': track_id, 'index': index},
                                    className='ms-3'
                                ),
                                dbc.Tooltip(
                                    'Add to queue',
                                    target={'type': 'to-queue', 'id': track_id, 'index': index},
                                    placement='left'
                                )
                            ],
                        ),
                        dbc.Collapse(
                            id={'type': 'to-queue-done', 'id': track_id},
                            children=[
                                html.I(className='bi bi-check ms-2')
                            ],
                            is_open=False
                        )
                    ],
                    className='d-flex flex-row flex-shrink-0'
                )
            ],
            className='d-flex justify-content-between align-items-center'
        )
