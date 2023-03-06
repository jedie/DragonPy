import socket
from unittest.mock import patch


def no_http_requests():
    """
    Deny any request in tests ;)
    """

    def side_effect(*args, **kwargs):
        raise RuntimeError(f'Missing request mock! args:{args} kwargs:{kwargs}')

    patch.object(socket, 'getaddrinfo', side_effect=side_effect).__enter__()
    patch.object(socket, 'create_connection', side_effect=side_effect).__enter__()
