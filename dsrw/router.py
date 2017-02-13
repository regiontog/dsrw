import functools

from .request import Request


class Router:
    INTERFACE = ('get_middleware', '_add_handler')

    def __init__(self):
        for attr in Router.INTERFACE:
            assert getattr(self, attr, None) is not None

        self.middleware = []

    def use(self, middleware):
        self.middleware.append(middleware.__middleware_instance__)

    def get(self, url):
        return self.route(Request.GET_METHODS, url)

    def post(self, url):
        return self.route(Request.POST_METHODS, url)

    def put(self, url):
        return self.route(Request.PUT_METHODS, url)

    def ns(self, route):
        return Namespace(self, route)

    def route(self, verbs, url):
        def decorator(fn):
            if not hasattr(fn, '__middleware__'):
                fn.__middleware__ = []

            middleware = [*fn.__middleware__, *self.get_middleware()]

            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                routines = [mw(*args, **kwargs) for mw in middleware]

                for routine in routines:
                    if next(routine) is False:
                        return

                fn(*args, **kwargs)

                for routine in reversed(routines):
                    try:
                        next(routine)
                        raise Exception('Misbehaving middleware')
                    except StopIteration:
                        pass

            self._add_handler(verbs, url, wrapper)
            return wrapper

        return decorator


class Namespace(Router):
    def __init__(self, parent, route):
        super().__init__()
        self.parent = parent
        self.url = route

    def _add_handler(self, verbs, url, fn):
        return self.parent._add_handler(verbs, self.url + url, fn)

    def get_middleware(self):
        return [*self.middleware, *self.parent.get_middleware()]
