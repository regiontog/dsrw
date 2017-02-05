# dsrw
Dead simple restful wsgi applications

# Installation

```pip install dsrw```

# Usage

```python
from wsgiref.simple_server import make_server
from dsrw import App, Request

app = App()


@app.get('/api/hello')
def hello(req: Request):
    return "Hello world!"


@app.get('/api/hello/:name')
def other(req: Request):
    return f"Hello {req.param.name}!"


@app.get('/api/echo')
def echo(req: Request):
    if req.has_valid_body:
        return req.body
    else:
        return "No body available"


if __name__ == '__main__':
    httpd = make_server('', 8080, app)
    print("Serving HTTP on port 8080...")

    # Respond to requests until process is killed
    httpd.serve_forever()

```

# Todo
- Headers
- Namespaces
- Cookies
- Middleware
- Query string
