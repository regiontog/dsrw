import http

from .constants import _CONTENT_ENC


class Response:
    DEFAULT_HEADERS = [('Content-type', 'application/json')]

    NOT_FOUND = http.HTTPStatus.NOT_FOUND, \
                [bytes(http.HTTPStatus.NOT_FOUND.description, _CONTENT_ENC)], \
                DEFAULT_HEADERS
    INTERNAL_ERR = http.HTTPStatus.INTERNAL_SERVER_ERROR, \
                   [bytes(http.HTTPStatus.INTERNAL_SERVER_ERROR.description, _CONTENT_ENC)], \
                   DEFAULT_HEADERS

    def __init__(self):
        self.headers = Response.DEFAULT_HEADERS[:]

    def add_header(self, key, value):
        self.headers.append((key, value))

    def cookie(self, name, value, **options):
        header_val = f"{name}={value}"

        for key in options:
            header_val += f"; {key}={options[key]}"

        self.add_header('Set-Cookie', header_val)

    def clear_cookie(self, name):
        self.cookie(name, "deleted", **{'Max-Age': 0})