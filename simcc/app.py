import os
from contextlib import asynccontextmanager
from http import HTTPStatus

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from simcc.config import Settings
from simcc.core.database import conn, get_conn
from simcc.routers import auth, institution, rbac, researcher
from simcc.routers.features import chat, collection, notification, star
from simcc.routers.users import uploads, users
from simcc.security import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    root_path=Settings().ROOT_PATH,
    docs_url='/swagger',
)

UPLOAD_DIR = 'simcc/storage/upload'
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    '/upload',
    StaticFiles(directory='simcc/storage/upload'),
    name='upload',
)

app.include_router(auth.router, tags=['authentication & authorization'])
app.include_router(
    users.router, tags=['authentication & authorization', 'account, base']
)

app.include_router(uploads.router, tags=['account, upload'])

app.include_router(institution.router, tags=['core, institution'])
app.include_router(researcher.router, tags=['core, researcher'])

app.include_router(collection.router, tags=['feature, collection'])
app.include_router(star.router, tags=['feature, star'])
app.include_router(rbac.router, tags=['feature, roles & permissions'])
app.include_router(notification.router, tags=['feature, notification'])
app.include_router(chat.router, tags=['feature, chat'])


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)


if Settings().PROD:

    @app.middleware('http')
    async def reverse_proxy(request: Request, call_next):
        response = await call_next(request)

        if response.status_code == HTTPStatus.NOT_FOUND:
            method_protected = request.method in {'POST', 'PUT', 'DELETE'}

            if method_protected:
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return Response(status_code=HTTPStatus.UNAUTHORIZED)

                token = auth_header.removeprefix('Bearer ').strip()

                try:
                    await get_current_user(token=token, conn=await get_conn())
                except Exception:
                    return Response(status_code=HTTPStatus.UNAUTHORIZED)

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


@app.get('/favicon.ico')
async def icon():
    return {'message': 'Working!'}
