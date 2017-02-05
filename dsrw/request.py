import logging
import ujson

from querystring_parser import parser

from .constants import _CONTENT_ENC
from .helper import lazy
from .response import Response

logger = logging.getLogger(__name__)


class Request:
    _JSON_TYPE_LEN = len('application/json')
    GET_METHODS = ('GET',)
    PUT_METHODS = ('PUT',)
    POST_METHODS = ('POST',)

    def __init__(self, env, path_params):
        self.env = env
        self.response = Response()
        self._path_param_type, self._path_param_vals = path_params

    @lazy
    def body(self):
        assert self.env['CONTENT_TYPE'][0:Request._JSON_TYPE_LEN] == 'application/json'

        try:
            len = int(self.env['CONTENT_LENGTH'])
        except ValueError:
            raise ValueError('Could not parse CONTENT_LENGTH {} into int'.format(self.env['CONTENT_LENGTH']))

        try:
            return ujson.loads(self.env['wsgi.input'].read(len))  # TODO: Buffer?
        except ValueError:
            raise ValueError('Malformed json body')

    @lazy
    def has_valid_body(self):
        try:
            nop = self.body
            return True
        except ValueError:
            return False
        except AssertionError:
            return False

    @lazy
    def param(self):
        # TODO: Parse ints?
        return self._path_param_type(*map(lambda n: n[0].decode(_CONTENT_ENC), self._path_param_vals))

    @lazy
    def cookies(self):
        cookies = self.env['HTTP_COOKIE'].split('; ')
        cookies = map(lambda cookie: cookie.split('='), cookies)

        return Cookies(**{cookie[0]: cookie[1] for cookie in cookies})

    @lazy
    def query(self):
        return QueryParam(parser.parse(self.env['QUERY_STRING']))


class QueryParam:
    def __init__(self, entries):
        self.__dict__.update({key: self.recursive_parse(entries[key]) for key in entries})

    def __getattr__(self, name):
        logger.warning(f'Access of undefined query parameter: {name}')
        return None

    @staticmethod
    def recursive_parse(value):
        if isinstance(value, dict):
            return QueryParam(value)
        else:
            return value

class Cookies:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __getattr__(self, name):
        logger.warning(f'Access of undefined cookie: {name}')
        return None
