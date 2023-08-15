import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

from ui.layout import modals

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
                dcc.Store(id='corrected-bpm-storage', storage_type='local'),
                html.Div(
                    id='header',
                    children=[
                        html.Img(
                            src=dash.get_asset_url('logos/Spotify_Logo_RGB_White.png'),
                            width=120,
                            className='py-2'
                        ),
                        html.Div(
                            children=[
                                html.Div(
                                    id='user-header',
                                    children=[],
                                    className='d-flex flex-row p-1'
                                ),
                                html.A(
                                    html.I(className='bi bi-gear h5'),
                                    id='local-settings',
                                    className='alt p-1 ms-1'
                                )
                            ],
                            className='d-flex flex-row align-items-center'
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
                                    size='sm',
                                    className='me-2'
                                ),
                                dbc.Button(
                                    id='filter',
                                    children=[
                                        html.I(className='bi bi-filter me-1'),
                                        'Filter'
                                    ],
                                    size='sm'
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
                modals.FilterSettings(),
                modals.LocalSettings(),
                modals.EditBPMValue()
            ],
            className='p-1'
        )
