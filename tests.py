import random
import string
import unittest

from app import App, enc


def nop():
    pass


def test_eq(url):
    return lambda x: x == url


def random_uri():
    parts_size = random.randint(2, 10)
    parts = []

    for _ in range(parts_size):
        str = ""
        for _ in range(random.randint(1, 16)):
            str += random.choice(string.ascii_letters)

        parts.append(str)

    return '/' + '/'.join(parts) + '/'


class BasicTests(unittest.TestCase):
    def test_one(self):
        app = App()

        num = 600
        for _ in range(num):
            url = random_uri()
            app.get(url)(test_eq(url))

        iters = 80
        for _ in range(iters):
            i = random.randint(0, num - 1)
            url = app.verbs['GET'][i][0]
            url = url.decode(enc)
            handler, params = app.dispatch('GET', url)
            self.assertIsNotNone(handler)
            self.assertTrue(handler(url))

    def test_wildcard(self):
        app = App()

        app.get('/:test/ayy')(nop)
        app.get('/two/ye')(nop)
        app.get('/:name/oscar')(nop)

        urls = ('/3/ayy', '/car/ayy', '/car/oscar', '/two/ye')
        for url in urls:
            handler, params = app.dispatch('GET', url)
            self.assertIsNotNone(handler)

    def url_parse_test(self):
        url, params = App.parse_url('/:name/test/:id/hello')
        self.assertEqual(url, b'/\0/test/\0/hello')
        self.assertEqual(params, [b'name', b'id'])

        url, params = App.parse_url('/mime/:param')
        self.assertEqual(url, b'/mime/\0')
        self.assertEqual(params, [b'param'])


if __name__ == '__main__':
    unittest.main()
