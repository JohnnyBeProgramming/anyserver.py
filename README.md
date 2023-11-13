# Simple Python Server

Simple and generic python web server, designed with simplicity and extendability in mind.

## Background & motivation

I really like the simplicity and elegance of frameworks like [`FastAPI`](https://fastapi.tiangolo.com/tutorial/first-steps/), [`Flask`](https://flask.palletsprojects.com/en/2.3.x/quickstart/#a-minimal-application), [`Express.js`](https://expressjs.com/en/starter/hello-world.html) and [`Koa.js`](https://koajs.com/#application).

```python
# Typical usage for defining routes
app = FastAPI() # Or some other framework like flask

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

What I don't like, for very simple use cases, is the _boilerplate_ and dependencies.

All of the above frameworks have some requirements and dependencies, meaning its not completely portable to all environments, without the need to download dependencies from the internet.

At its core, this project was designed with the following features in mind:

- Handle `HTTP` routes with a simple `request` - `response` model.
- Support ways to serve static content from a folder (eg: HTML, CSS, JS).
- A zero-dependency `server.py` that just works out of the box as a simple web server.
- Supports multiple response types, with ability to render custom templated responses.

With these basic requirements in place, rapid prototyping is possible with very little overhead.
