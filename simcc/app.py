import os
from contextlib import asynccontextmanager
from http import HTTPStatus

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from simcc.config import Settings
from simcc.core.database import conn
from simcc.routers import auth, keys, rbac, researcher
from simcc.routers.departament import uploads as d_uploads
from simcc.routers.features import chat, notification, star
from simcc.routers.features.collection import collection
from simcc.routers.features.collection import upload as c_uploads
from simcc.routers.group import group
from simcc.routers.group import upload as rg_uploads
from simcc.routers.institution import institution
from simcc.routers.institution import uploads as i_uploads
from simcc.routers.program import upload as p_uploads
from simcc.routers.users import uploads as u_uploads
from simcc.routers.users import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    root_path=Settings().ROOT_PATH_ADMIN,
    docs_url='/swagger',
)

UPLOAD_DIR = 'simcc/storage/upload'
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount(
    '/upload',
    StaticFiles(directory='simcc/storage/upload'),
    name='upload',
)

app.include_router(auth.router, tags=['Authentication'])
app.include_router(user.router, tags=['User Management'])
app.include_router(keys.router, tags=['Key Management'])

app.include_router(u_uploads.router, tags=['User Uploads'])
app.include_router(i_uploads.router, tags=['Institution Uploads'])
app.include_router(c_uploads.router, tags=['Collection Uploads'])
app.include_router(p_uploads.router, tags=['Program Uploads'])
app.include_router(rg_uploads.router, tags=['Group Uploads'])
app.include_router(d_uploads.router, tags=['Dep Uploads'])

app.include_router(institution.router, tags=['Institution'])
app.include_router(researcher.router, tags=['Researcher'])
app.include_router(group.router, tags=['Group'])

app.include_router(collection.router, tags=['Collection'])
app.include_router(star.router, tags=['Star'])
app.include_router(rbac.router, tags=['Roles & Permissions'])
app.include_router(notification.router, tags=['Notification'])
app.include_router(chat.router, tags=['Chat'])


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
            async with httpx.AsyncClient() as client:
                headers = {
                    k: v
                    for k, v in request.headers.items()
                    if k.lower() not in {'host', 'content-length'}
                }
                proxy_response = await client.request(
                    method=request.method,
                    url=f'{Settings().PROXY_ADMIN_URL}{request.url.path}',
                    params=dict(request.query_params),
                    headers=headers,
                    content=await request.body(),
                    timeout=None,
                )
                excluded_headers = [
                    'content-encoding',
                    'transfer-encoding',
                    'connection',
                ]
                response_headers = {
                    k: v
                    for k, v in proxy_response.headers.items()
                    if k.lower() not in excluded_headers
                }

                return Response(
                    content=proxy_response.content,
                    status_code=proxy_response.status_code,
                    headers=response_headers,
                )

        return response


@app.get('/')
async def read_root():
    return {'message': 'Working!'}


@app.get('/favicon.ico')
async def icon():
    return {'message': 'Working!'}
