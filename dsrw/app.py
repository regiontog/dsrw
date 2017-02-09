import bisect
import http
import logging
import ujson
from collections import defaultdict, namedtuple

from .constants import _CONTENT_ENC, _COLON, _WILDCARD, _ENC, _SLASH
from .request import Request
from .response import Response
from .router import Router

logger = logging.getLogger(__name__)


class App(Router):
    def __init__(self):
        self.verbs = defaultdict(lambda: [])

    def __call__(self, env, start_response):
        try:
            fn, path_params = self.dispatch(env['REQUEST_METHOD'], env['SCRIPT_NAME'] + env['PATH_INFO'])

            if fn is not None:
                req = Request(env, path_params)
                result = fn(req)
                headers = req.response.headers
                if isinstance(result, tuple):
                    code, content = result[0], [bytes(ujson.dumps(result[1]), _CONTENT_ENC)]
                else:
                    code, content = http.HTTPStatus.OK, [bytes(ujson.dumps(result), _CONTENT_ENC)]
            else:
                code, content, headers = Response.NOT_FOUND
        except Exception:
            logger.exception('Internal Server Error')
            code, content, headers = Response.INTERNAL_ERR

        start_response(f"{code.value} {code.phrase}", headers)
        return content

    def dispatch(self, verb, url):
        routes = self.verbs[verb]
        routes_len = len(routes)
        route_index = 0
        route_char_index = 0
        url_char_index = 0
        url_bytes = bytes(url, _ENC)
        url_bytes_len = len(url_bytes)
        param_stack = []

        while True:
            try:
                if url_bytes[url_char_index] == routes[route_index][0][route_char_index]:
                    route_char_index += 1
                    url_char_index += 1
                elif routes[route_index][0][route_char_index] == _WILDCARD:
                    item = (bytearray(), url_char_index, route_char_index)
                    param_stack.append(item)
                    route_char_index += 1
                    while url_bytes[url_char_index] != _SLASH:
                        item[0].append(url_bytes[url_char_index])
                        url_char_index += 1

                elif url_bytes[url_char_index] > routes[route_index][0][route_char_index]:
                    route_index += 1
                    if len(param_stack) > 0:
                        _, url_char_index, route_char_index = param_stack.pop()
                else:
                    return None, "Smaller than current (but we've already looked through all smaller than current)"
            except IndexError:
                if route_index >= routes_len:
                    return None, "End of routes"

                if url_bytes_len == url_char_index and len(routes[route_index][0]) == route_char_index:
                    return routes[route_index][1], (routes[route_index][2], param_stack)
                else:
                    route_index += 1
                    if len(param_stack) > 0:
                        _, url_char_index, route_char_index = param_stack.pop()

    @staticmethod
    def parse_url(url):
        res = bytearray()
        b_url = bytes(url, _ENC)
        params = []
        l = len(b_url)
        i = 0
        while i < l:
            if b_url[i] == _COLON and b_url[i - 1] == _SLASH:
                params.append("")
                i += 1
                while i < l and b_url[i] != _SLASH:
                    params[-1] += url[i]
                    i += 1

                res.append(_WILDCARD)
            else:
                res.append(b_url[i])
                i += 1

        return res, params

    @staticmethod
    def normalize_verb(verb: str):
        return verb.upper()

    def _route(self, verbs, url, handler):
        url, params = self.parse_url(url)
        params_type = namedtuple('PathParams', params)

        for verb in verbs:
            bisect.insort(self.verbs[self.normalize_verb(verb)], (url, handler, params_type))

    def route(self, verbs, url):
        def decorator(fn):
            self._route(verbs, url, fn)
            return fn

        return decorator
