import dash_bootstrap_components as dbc
from dash import html

from ui.layout.layout import IMG_SIZE


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
                        html.Img(src=img_url, width=IMG_SIZE, height=IMG_SIZE),
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
                            className='bi bi-three-dots-vertical ms-1 px-1',
                            id={'type': 'stats', 'id': track_id}
                        ),
                        dbc.Popover(
                            id={'type': 'stats-popover', 'id': track_id},
                            children=[
                                dbc.PopoverHeader(
                                    html.A(
                                        children=[
                                            html.I(className='bi bi-pencil-square me-2'),
                                            'Edit bpm'
                                        ],
                                        id={'type': 'edit-bpm', 'id': track_id},
                                        className='alt'
                                    )
                                ),
                                html.Div(
                                    dbc.Table(
                                        html.Tbody([
                                            html.Tr([html.Td('Acousticness'), html.Td(f'{round(acousticness * 100)}%')]),
                                            html.Tr([html.Td('Danceability'), html.Td(f'{round(danceability * 100)}%')]),
                                            html.Tr([html.Td('Energy'), html.Td(f'{round(energy * 100)}%')]),
                                            html.Tr([html.Td('Instrumentalness'), html.Td(f'{round(instrumentalness * 100)}%')]),
                                            html.Tr([html.Td('Valence'), html.Td(f'{round(valence * 100)}%')]),
                                        ]),
                                        borderless=True,
                                        className='compact'
                                    ),
                                    className='p-2'
                                )
                            ],
                            target={'type': 'stats', 'id': track_id},
                            placement='left',
                            trigger='hover'
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
