# dsrw
Dead simple restful wsgi applications

# Installation

```pip install dsrw```

#Usage
## REST

```python
from wsgiref.simple_server import make_server
from dsrw import App, Request
from dsrw import middleware

app = App()
app.use(middleware.json)
users = []


@app.get('/user')
def hello(req: Request):
    return users
    
@app.post('/user')
def echo(req: Request):
    return users.append(req.body)

if __name__ == '__main__':
    httpd = make_server('', 8080, app)
    print("Serving HTTP on port 8080...")

    # Respond to requests until process is killed
    httpd.serve_forever()

```

## Path parameters
```python
from wsgiref.simple_server import make_server
from dsrw import App, Request

app = App()


@app.get('/hello/:name')
def hello(req: Request):
    return req.param.name
    
# Server ...
```

## Namespaces
```python
from wsgiref.simple_server import make_server
from dsrw import App, Request
from dsrw import middleware

app = App()
users = [{'name': "bill", 'desc': "This is bill."}]


@app.get('/hello/:name')
def hello(req: Request):
    return req.param.name
    

api = app.ns('/api')
api.use(middleware.json)


@api.get('/user/:id')
def show(req: Request):
    return users[req.param.id]
 
# Server ...
```

## Middleware
```python
from wsgiref.simple_server import make_server
from dsrw import App, Request
from dsrw import middleware

import random


@middleware.new
def my_middleware(req: Request):
    print(req)
    yield
    print(req.response.status)
  
  
def cat_fact():
    return random.choice((
        "Did you know that the first cat show was held in 1871 at the Crystal Palace in London? Mee-wow!",
        "Cats, especially older cats, do get cancer. Many times this disease can be treated successfully.",
        "Cats can't taste sweets.",
        "Cats must have fat in their diet because they can't produce it on their own."
    ))
        
@middleware.new
def cat_facts(req: Request):
    req.add(cat_fact)
    yield


app = App()
app.use(my_middleware)

@app.get('/hello')
def hello(req: Request):
    return b"Hello world"
    

@app.get('/fact')
@cat_facts
def hello(req: Request):
    return req.cat_fact
    
# Server ...
```

# Todo
- Modules
