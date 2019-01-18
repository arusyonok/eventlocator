import urllib.parse
from flask import session
from common import call

NOMINATIM_URL = 'http://nominatim.openstreetmap.org/reverse'


def is_logged_in():
    return session.get('username', None)


def get_artists(spotify):
    followed_artists = spotify.get_user_followed_artists()
    top_artists = spotify.get_user_top_artists()

    all_artists = []
    artist_names = []

    for f_artist in followed_artists['artists']['items']:
        artist_names.append(f_artist['name'])
        all_artists.append({
            'name': f_artist['name'] or '',
            'spotify_url': f_artist['external_urls']['spotify'] or '#',
            'image_url': f_artist['images'][0]['url'] or '#',
            'genres': f_artist['genres'] or [],
            'user_relation': 'Followed Artist'
        })

    f_artist_names = [artist['name'] for artist in all_artists]

    for t_artist in top_artists['items']:
        if t_artist['name'] in f_artist_names:
            continue

        all_artists.append({
            'name': t_artist['name'] or '',
            'spotify_url': t_artist['external_urls']['spotify'] or '#',
            'image_url': t_artist['images'][0]['url'] or '#',
            'genres': t_artist['genres'] or [],
            'user_relation': 'Top Artist'
        })

    return all_artists


def get_country_code(latitude, longitude):
    payload = {
        'lat': latitude,
        'lon': longitude,
        'format': 'jsonv2'
    }

    urlparams = urllib.parse.urlencode(payload)
    url = "%s?%s" % (NOMINATIM_URL, urlparams)
    response = call('get', url)
    response_json = response.json()

    if 'address' in response_json.keys() and 'country_code' in response_json['address']:
        return response_json['address']['country_code']

    return None
