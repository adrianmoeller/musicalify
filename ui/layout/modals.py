import dash_bootstrap_components as dbc
from dash import html, dcc


class FilterSettings(dbc.Modal):
    def __init__(self):
        super().__init__(
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


class LocalSettings(dbc.Modal):
    def __init__(self):
        super().__init__(
            id='local-settings-modal',
            children=[
                dbc.ModalHeader(dbc.ModalTitle('Settings')),
                dbc.ModalBody([
                    dbc.Card(
                        children=[
                            dbc.CardHeader(
                                children=[
                                    'Number of BPM values stored:',
                                    html.Div(id='num-bpm-values', className='ms-2')
                                ],
                                className='d-flex'
                            ),
                            dbc.CardBody(
                                children=[
                                    dcc.Upload(
                                        dbc.Button('Import', id='import-bpm-values'),
                                        id='import-bpm-values-uploader',
                                        accept='.musicalify.json',
                                        max_size=5242880,  # =5MB
                                        className='me-3'
                                    ),
                                    dbc.Button('Export', id='export-bpm-values'),
                                    dcc.Download(id='export-bpm-values-downloader')
                                ],
                                className='d-flex'
                            )
                        ],
                        color='primary',
                        outline=True,
                        className='mb-3'
                    ),
                    dbc.Card(
                        children=[
                            dbc.CardBody(
                                children=[
                                    'Reset all manually corrected BPM values:',
                                    dbc.Button(
                                        'Reset',
                                        id='reset-corrected-bpm',
                                        color='danger'
                                    ),
                                    ResetBPMValuesPrompt()
                                ],
                                className='d-flex justify-content-between align-items-center'
                            )
                        ],
                        color='danger',
                        outline=True
                    )
                ])
            ],
            centered=True,
            is_open=False
        )


class ResetBPMValuesPrompt(dbc.Modal):
    def __init__(self):
        super().__init__(
            id='reset-bpm-prompt',
            children=[
                dbc.ModalBody('You are going to delete all stored BPM corrections. This cannot be undone. Are you sure?'),
                dbc.ModalFooter([
                    dbc.Button(
                        'Cancel',
                        id='reset-corrected-bpm-cancel',
                    ),
                    dbc.Button(
                        'Delete',
                        id='reset-corrected-bpm-prompt',
                        color='danger'
                    )
                ])
            ],
            centered=True,
            is_open=False
        )


class EditBPMValue(dbc.Modal):
    def __init__(self):
        super().__init__(
            id='edit-bpm-value-modal',
            children=[
                dbc.ModalHeader(dbc.ModalTitle('Edit bpm value')),
                dbc.ModalBody([
                    html.P('If the bpm value for this track does not seem correct, a custom value can be provided, which will be locally stored in the browser. Leave blank to reset.'),
                    dbc.InputGroup(
                        children=[
                            dbc.InputGroupText('New value:'),
                            dbc.Input(id='edit-bpm-value-input', type='number', min=0, class_name='bpm-input'),
                            dbc.InputGroupText('bpm')
                        ]
                    ),
                    html.Div(id='edit-bpm-value-track-id', className='d-none')
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        children='Save',
                        id='edit-bpm-value-save'
                    )
                ])
            ],
            centered=True,
            is_open=False
        )
