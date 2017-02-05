import ujson

from .constants import _CONTENT_ENC
from .helper import lazy


class Request:
    _JSON_TYPE_LEN = len('application/json')
    GET_METHODS = ('GET',)
    PUT_METHODS = ('PUT',)
    POST_METHODS = ('POST',)

    def __init__(self, env, path_params):
        self.env = env
        self.path_param_type, self.path_param_vals = path_params

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
        return self.path_param_type(*map(lambda n: n[0].decode(_CONTENT_ENC), self.path_param_vals))
