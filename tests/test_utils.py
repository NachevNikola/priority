import json


def make_request(client, method, url, token=None, data=None):
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'
    if data is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data)

    client_method = getattr(client, method.lower())

    return client_method(url, headers=headers, data=data)
