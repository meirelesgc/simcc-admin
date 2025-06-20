from contextlib import asynccontextmanager
from http import HTTPStatus

import httpx
from fastapi import FastAPI, Request, Response

from simcc.config import Settings
from simcc.core.database import conn
from simcc.routers import auth, institution, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(lifespan=lifespan, docs_url='/swagger')

app.include_router(auth.router, tags=['Authentication'])
app.include_router(users.router, tags=['Users'])
app.include_router(institution.router, tags=['Institution'])


@app.middleware('http')
async def reverse_proxy(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == HTTPStatus.NOT_FOUND:
        async with httpx.AsyncClient() as client:
            proxy_response = await client.request(
                method=request.method,
                url=f'{Settings().PROXY_URL}{request.url.path}',
                params=request.query_params,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=None,
            )
            return Response(
                content=proxy_response.content,
                status_code=proxy_response.status_code,
                headers=dict(proxy_response.headers),
            )
    return response


@app.get('/')
async def read_root():
    return {'message': 'Working!'}
