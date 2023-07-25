SPOTIFY_URI_START = 'https://open.spotify.com/'
TRACK_IDENTIFIER = '/track/'
ALBUM_IDENTIFIER = '/album/'
PLAYLIST_IDENTIFIER = '/playlist/'
PARAMETER_IDENTIFIER = '?'


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
