import requests
from app import errors


def call(method, url, **kwargs):
    if method == 'get':
        response = requests.get(url, **kwargs)
    elif method == 'post':
        response = requests.post(url, **kwargs)
    else:
        raise Exception('Please specify call method.')

    if response.status_code is 200:
        return response

    code_message = str(response.status_code) + ' ' + str(response.reason)
    raise errors.ResponseException(code_message)


