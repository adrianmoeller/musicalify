import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

IMG_SIZE = 50


class Layout(html.Div):
    def __init__(self):
        super().__init__(
            id='layout',
            children=[
                dcc.Location(id='url'),
                dcc.Store(id='content-storage', storage_type='session'),
                dcc.Store(id='to-queue-done-storage', storage_type='session'),
                dcc.Store(id='filter-settings', storage_type='session'),
                dcc.Store(id='bpm-sort-state', storage_type='session'),
                html.Div(
                    id='header',
                    children=[
                        html.Img(
                            src=dash.get_asset_url('logos/Spotify_Logo_RGB_White.png'),
                            width=120,
                            className='py-2'
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
                        html.Div(
                            id='content-title',
                            className='d-flex justify-content-center'
                        ),
                        html.Div(
                            children=[
                                dbc.Button(
                                    id='sort',
                                    children=[
                                        html.I(
                                            id='sort-icon',
                                            className='bi bi-arrow-down-up me-1'
                                        ),
                                        'Sort by BPM'
                                    ],
                                    className='me-2'
                                ),
                                dbc.Button(
                                    id='filter',
                                    children=[
                                        html.I(className='bi bi-filter me-1'),
                                        'Filter'
                                    ]
                                )
                            ],
                            className='p-1 d-flex justify-content-end'
                        ),
                        dbc.ListGroup(
                            id='tracks',
                            className='p-1'
                        ),
                        html.Div(
                            children=[
                                dbc.Pagination(
                                    id='pager',
                                    previous_next=True,
                                    max_value=1,
                                    class_name='d-none'
                                )
                            ],
                            className='d-flex justify-content-center sticky-btm'
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
                            className='p-4 d-flex justify-content-center'
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
                ),
                dbc.Modal(
                    id='filter-modal',
                    children=[
                        dbc.ModalHeader(dbc.ModalTitle('Filter settings')),
                        dbc.ModalBody([
                            dbc.InputGroup(
                                children=[
                                    dbc.InputGroupText(dbc.Checkbox(id='check-filter-greater')),
                                    dbc.InputGroupText('Lower bound:'),
                                    dbc.Input(id='filter-greater-input', type='number', min=0, class_name='bpm-input'),
                                    dbc.InputGroupText('bpm')
                                ],
                                class_name='mb-2'
                            ),
                            dbc.InputGroup(
                                children=[
                                    dbc.InputGroupText(dbc.Checkbox(id='check-filter-smaller')),
                                    dbc.InputGroupText('Upper bound:'),
                                    dbc.Input(id='filter-smaller-input', type='number', min=0, class_name='bpm-input'),
                                    dbc.InputGroupText('bpm')
                                ],
                                class_name='mb-3'
                            ),
                            dbc.InputGroup(
                                children=[
                                    dbc.InputGroupText('Double bpm smaller then:'),
                                    dbc.Input(id='double-smaller-input', type='number', min=0, class_name='bpm-input'),
                                    dbc.InputGroupText('bpm')
                                ],
                                class_name='mb-2'
                            ),
                            dbc.InputGroup(
                                children=[
                                    dbc.InputGroupText('Half bpm greater then:'),
                                    dbc.Input(id='half-greater-input', type='number', min=0, class_name='bpm-input'),
                                    dbc.InputGroupText('bpm')
                                ]
                            )
                        ])
                    ],
                    centered=True,
                    is_open=False
                )
            ],
            className='p-1'
        )


class TrackTile(dbc.ListGroupItem):
    def __init__(self,
                 title: str,
                 artist: str,
                 img_url: str,
                 track_id: str,
                 tempo: float,
                 acousticness: float,
                 danceability: float,
                 energy: float,
                 instrumentalness: float,
                 valence: float
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
                        html.I(
                            className='bi bi-graph-up ms-2 px-1',
                            id={'type': 'stats', 'id': track_id}
                        ),
                        dbc.Tooltip(
                            children=[
                                html.Div(f'Acousticness: {round(acousticness * 100)}%'),
                                html.Div(f'Danceability: {round(danceability * 100)}%'),
                                html.Div(f'Energy: {round(energy * 100)}%'),
                                html.Div(f'Instrumentalness: {round(instrumentalness * 100)}%'),
                                html.Div(f'Valence: {round(valence * 100)}%')
                            ],
                            target={'type': 'stats', 'id': track_id},
                            placement='left'
                        ),
                        html.Div(
                            children=[
                                html.A(
                                    html.I(className='bi bi-view-stacked'),
                                    id={'type': 'to-queue', 'id': track_id},
                                    className='ms-4 p-1'
                                ),
                                dbc.Tooltip(
                                    'Add to queue',
                                    target={'type': 'to-queue', 'id': track_id},
                                    placement='left'
                                )
                            ],
                        ),
                        dbc.Collapse(
                            id={'type': 'to-queue-done', 'id': track_id},
                            children=[
                                html.I(className='bi bi-check')
                            ],
                            dimension='width',
                            is_open=False
                        )
                    ],
                    className='d-flex flex-row flex-shrink-0'
                )
            ],
            className='d-flex justify-content-between align-items-center'
        )
