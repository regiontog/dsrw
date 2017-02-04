import bisect
import http
from collections import defaultdict

enc = 'ascii'
star = 0
_star = bytes('*', enc)[0]
slash = bytes('/', enc)[0]


def convert_stars(c):
    if c == _star:
        return star
    elif c == star:
        return _star
    else:
        return c


def normalize_verb(verb: str):
    return verb.upper()


class App:
    GET_METHODS = ('GET',)
    PUT_METHODS = ('PUT',)
    POST_METHODS = ('POST',)
    HEADERS = [('Content-type', 'text/plain')]

    def __init__(self):
        self.verbs = defaultdict(lambda: [])

    def __call__(self, env, start_response):
        try:
            fn, path_params = self.dispatch(env['REQUEST_METHOD'], env['SCRIPT_NAME'])

            if fn is not None:
                result = fn()
                if isinstance(result, tuple):
                    code, content = result
                else:
                    code, content = http.HTTPStatus.OK, result
            else:
                code, content = http.HTTPStatus.NOT_FOUND, ""
        except Exception:
            code, content = http.HTTPStatus.INTERNAL_SERVER_ERROR, ""

        start_response("{value} {phrase}".format(code), App.HEADERS)
        return [content]

    # @profile
    def dispatch(self, verb, url):
        routes = self.verbs[verb] # TODO: Normalize verb?
        route_index = 0
        route_char_index = 0
        url_char_index = 0
        url_bytes = bytes(url, enc)
        star_stack = []

        try:
            while True:
                if url_bytes[url_char_index] == routes[route_index][0][route_char_index]:
                    route_char_index += 1
                    url_char_index += 1
                elif routes[route_index][0][route_char_index] == star:
                    item = (url_char_index, bytearray())
                    route_char_index += 1
                    while url_bytes[url_char_index] != slash:
                        item[1].append(url_bytes[url_char_index])
                        url_char_index += 1

                    star_stack.append(item)
                elif url_bytes[url_char_index] > routes[route_index][0][route_char_index]:
                    route_index += 1
                    if len(star_stack) > 0:
                        pos, _ = star_stack.pop()
                        route_char_index = pos
                        url_char_index = pos
                else:
                    return None, "Smaller than prev"
        except IndexError:
            if len(routes[route_index][0]) == route_char_index:
                return routes[route_index][1], map(lambda it: it[1], star_stack)
            else:
                return None, "IndexError"

    def _route(self, verbs, url, handler):
        url = bytes(url, enc)
        url = bytes(map(convert_stars, url))
        for verb in verbs:
            bisect.insort(self.verbs[normalize_verb(verb)], (url, handler))

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