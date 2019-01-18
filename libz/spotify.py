import base64
import os
import time
import urllib.parse
import json
from werkzeug.contrib.cache import SimpleCache

from config import SPOTIFY_REDIRECT_URI, SPOTIFY_CLIENT_SECRET, SPOTIFY_CLIENT_ID
from common import call

simpleCacheObject = SimpleCache()

SPOTIFY_SCOPE = "user-read-private user-follow-read user-top-read"
SPOTIFY_API_URL = 'https://api.spotify.com/v1/'

OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize/'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token/'


class SpotifyException(Exception):
    pass


class Spotify:

    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self.redirect_uri = SPOTIFY_REDIRECT_URI
        self.scope = SPOTIFY_SCOPE
        self.api_url = SPOTIFY_API_URL
        self.authorisation_url = OAUTH_AUTHORIZE_URL
        self.token_url = OAUTH_TOKEN_URL
        self.token_info = None
        self.cache_dir = os.path.dirname(os.path.realpath(__file__)) + '/spotify-cache-dir/'
        self.cache_filename_ext = '-token.cache'
        self.cache_filepath = None

    def get_authorisation_url(self):
        payload = {'client_id': self.client_id,
                   'response_type': 'code',
                   'redirect_uri': self.redirect_uri,
                    'scope': self.scope}

        urlparams = urllib.parse.urlencode(payload)

        return "%s?%s" % (self.authorisation_url, urlparams)

    def set_token_info(self, code):
        if code is None:
            raise SpotifyException('Code has not been provided.')

        data = {
            'redirect_uri': self.redirect_uri,
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        params = {'data': data, 'verify': True}

        self.token_info = self._get_new_token_info(params)

    def _get_new_token_info(self, params):
        response = call('post', self.token_url, **params)
        token_info = response.json()
        token_info['expires_at'] = int(time.time()) + token_info['expires_in']
        token_info['scope'] = self.scope

        return token_info

    def store_token_info(self):
        if self.token_info is None:
            raise SpotifyException('Token info have not been provided.')

        user = self.get_user_information()
        username = user['display_name']
        self.cache_filepath = self.cache_dir + username + self.cache_filename_ext
        simpleCacheObject.set_many(self.token_info)

        try:
            os.makedirs(os.path.dirname(self.cache_filepath), exist_ok=True)
            file = open(self.cache_filepath, 'w+')
            file.write(json.dumps(self.token_info))
            file.close()
        except IOError:
            raise SpotifyException('Could not store the access token.')

    def get_access_token(self):
        if self.token_info and not self._is_expired():
            return self.token_info['access_token']

        if simpleCacheObject.get('access_token'):
            return simpleCacheObject.get('access_token')

        if self.cache_filepath:
            self.token_info = self._get_cached_token()
        else:
            data = {'grant_type': 'client_credentials'}
            params = {'data': data, 'verify': True, 'headers': self._auth_header_token()}
            self.token_info = self._get_new_token_info(params)
            self.store_token_info()

        return self.token_info['access_token']

    def _get_cached_token(self):
        try:
            file = open(self.cache_filepath, 'r')
            cached_token = json.loads(file.read())
            file.close()
            return cached_token
        except IOError:
            raise SpotifyException('Could not find the access token.')

    def get_user_information(self):
        params = {'headers' : self._auth_headers()}
        response = call('get', self.api_url + 'me/', **params)

        return response.json()

    def get_user_followed_artists(self):
        params = {'headers': self._auth_headers()}
        response = call('get', self.api_url + 'me/following?type=artist', **params)

        return response.json()

    def get_user_top_artists(self):
        params = {'headers': self._auth_headers()}
        response = call('get', self.api_url + 'me/top/artists', **params)

        return response.json()

    def _auth_header_token(self):
        auth_header = base64.b64encode(str(self.client_id + ':' + self.client_secret).encode())
        headers = {'Authorization': 'Basic {}'.format(auth_header.decode())}

        return headers

    def _auth_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.get_access_token()),
            'Content-Type': 'application/json',
        }

        return headers

    def clear_cache(self):
        simpleCacheObject.clear()
        if self.cache_filepath:
            os.remove(self.cache_filepath)
        return True

    def _is_expired(self):
        return self.token_info['expires_at'] < int(time.time())
