from typing import Any

from spotipy import Spotify

from ui.layout import IMG_SIZE

MAX_TRACK_REQ_NO = 50
MAX_FEATURE_REQ_NO = 100


def get_content(spotify: Spotify, track_id: str) -> dict:
    track = get_tracks(spotify, [track_id])[0]
    features = get_features(spotify, [track_id])[0]
    return extract_data(track, features)


def get_contents(spotify: Spotify, tracks: list[dict], img_url=None) -> list[dict]:
    if not tracks:
        return list()

    features = get_features(spotify, [track['id'] for track in tracks])

    result = list()
    for idx in range(len(tracks)):
        result.append(extract_data(tracks[idx], features[idx], img_url))

    return result


def extract_data(track: dict, features: dict, img_url=None):
    track_data = dict()
    track_data['title'] = track['name']
    track_data['artist'] = ', '.join(artist['name'] for artist in track['artists'])
    track_data['img_url'] = img_url if img_url else choose_image_url(track['album']['images'])
    track_data['track_id'] = track['uri']
    track_data['tempo'] = features['tempo']
    track_data['acousticness'] = features['acousticness']
    track_data['danceability'] = features['danceability']
    track_data['energy'] = features['energy']
    track_data['instrumentalness'] = features['instrumentalness']
    track_data['valence'] = features['valence']
    return track_data


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


def choose_image_url(images: list[dict], min_height: int = IMG_SIZE) -> str:
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
