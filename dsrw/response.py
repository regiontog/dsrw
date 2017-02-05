import http

from .constants import _CONTENT_ENC


class Response:
    HEADERS = [('Content-type', 'application/json')]

    NOT_FOUND = http.HTTPStatus.NOT_FOUND, [bytes(http.HTTPStatus.NOT_FOUND.description, _CONTENT_ENC)]
    INTERNAL_ERR = http.HTTPStatus.INTERNAL_SERVER_ERROR, [
        bytes(http.HTTPStatus.INTERNAL_SERVER_ERROR.description, _CONTENT_ENC)]
