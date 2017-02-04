import dsrw
from flipflop import WSGIServer

app = dsrw.App()


@app.get("/hello")
def hello_world():
    return b"Hello World"

if __name__ == '__main__':
    WSGIServer(app).run()