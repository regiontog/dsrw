import bisect
import logging

import http
import traceback
from collections import defaultdict, namedtuple

import ujson
from .helper import lazy

logger = logging.getLogger(__name__)

enc = 'ascii'
wildcard = 0
slash = bytes('/', enc)[0]
colon = bytes(':', enc)[0]


def normalize_verb(verb: str):
    return verb.upper()


class App:
    GET_METHODS = ('GET',)
    PUT_METHODS = ('PUT',)
    POST_METHODS = ('POST',)
    HEADERS = [('Content-type', 'application/json')]
    CONTENT_ENC = 'utf-8'

    def __init__(self):
        self.verbs = defaultdict(lambda: [])

    def __call__(self, env, start_response):
        try:
            fn, path_params = self.dispatch(env['REQUEST_METHOD'], env['SCRIPT_NAME'] + env['PATH_INFO'])

            if fn is not None:
                req = Request(env, path_params)
                result = fn(req)
                if isinstance(result, tuple):
                    code, content = result[0], [bytes(ujson.dumps(result[1]), App.CONTENT_ENC)]
                else:
                    code, content = http.HTTPStatus.OK, [bytes(ujson.dumps(result), App.CONTENT_ENC)]
            else:
                code, content = Response.NOT_FOUND
        except Exception:
            logger.exception('Internal Server Error')
            code, content = Response.INTERNAL_ERR

        start_response(f"{code.value} {code.phrase}", App.HEADERS)
        return content

    def dispatch(self, verb, url):
        routes = self.verbs[verb]
        route_index = 0
        route_char_index = 0
        url_char_index = 0
        url_bytes = bytes(url, enc)
        param_stack = []
        item = None

        while True:
            try:
                if url_bytes[url_char_index] == routes[route_index][0][route_char_index]:
                    route_char_index += 1
                    url_char_index += 1
                elif routes[route_index][0][route_char_index] == wildcard:
                    item = (bytearray(), url_char_index, route_char_index)
                    route_char_index += 1
                    while url_bytes[url_char_index] != slash:
                        item[0].append(url_bytes[url_char_index])
                        url_char_index += 1

                    param_stack.append(item)
                    item = None
                elif url_bytes[url_char_index] > routes[route_index][0][route_char_index]:
                    route_index += 1
                    if len(param_stack) > 0:
                        _, url_char_index, route_char_index = param_stack.pop()
                else:
                    return None, "Smaller than current (but we've already looked through all smaller than current)"
            except IndexError:
                if item is not None:
                    param_stack.append(item)
                if route_index >= len(routes):
                    return None, "End of routes"

                if len(routes[route_index][0]) == route_char_index:
                    return routes[route_index][1], (routes[route_index][2], param_stack)
                else:
                    route_index += 1
                    if len(param_stack) > 0:
                        _, url_char_index, route_char_index = param_stack.pop()

    @staticmethod
    def parse_url(url):
        res = bytearray()
        b_url = bytes(url, enc)
        params = []
        l = len(b_url)
        i = 0
        while i < l:
            if b_url[i] == colon and b_url[i - 1] == slash:
                params.append("")
                i += 1
                while i < l and b_url[i] != slash:
                    params[-1] += url[i]
                    i += 1

                res.append(wildcard)
            else:
                res.append(b_url[i])
                i += 1

        return res, params

    def _route(self, verbs, url, handler):
        url, params = self.parse_url(url)
        params_type = namedtuple('PathParams', params)

        for verb in verbs:
            bisect.insort(self.verbs[normalize_verb(verb)], (url, handler, params_type))

    def route(self, verbs, url):
        def decorator(fn):
            self._route(verbs, url, fn)
            return fn

        return decorator

    def get(self, url):
        return self.route(App.GET_METHODS, url)

    def post(self, url):
        return self.route(App.POST_METHODS, url)

    def put(self, url):
        return self.route(App.PUT_METHODS, url)


class Response:
    NOT_FOUND = http.HTTPStatus.NOT_FOUND, [bytes(http.HTTPStatus.NOT_FOUND.description, App.CONTENT_ENC)]
    INTERNAL_ERR = http.HTTPStatus.INTERNAL_SERVER_ERROR, [
        bytes(http.HTTPStatus.INTERNAL_SERVER_ERROR.description, App.CONTENT_ENC)]


class Request:
    JSON_TYPE_LEN = len('application/json')

    def __init__(self, env, path_params):
        self.env = env
        self.path_param_type, self.path_param_vals = path_params

    @lazy
    def body(self):
        assert self.env['CONTENT_TYPE'][0:Request.JSON_TYPE_LEN] == 'application/json'

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
        return self.path_param_type(*map(lambda n: n[0].decode(App.CONTENT_ENC), self.path_param_vals))
