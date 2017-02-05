from .request import Request


class Router:
    def get(self, url):
        return self.route(Request.GET_METHODS, url)

    def post(self, url):
        return self.route(Request.POST_METHODS, url)

    def put(self, url):
        return self.route(Request.PUT_METHODS, url)

    def ns(self, route):
        return Namespace(self, route)


class Namespace(Router):
    def __init__(self, parent, route):
        self.parent = parent
        self.url = route

    def route(self, verbs, url):
        return self.parent.route(verbs, self.url + url)
