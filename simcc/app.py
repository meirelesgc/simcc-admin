from contextlib import asynccontextmanager

from fastapi import FastAPI

from simcc.core.database import conn
from simcc.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(lifespan=lifespan, docs_url='/swagger')

app.include_router(auth.router, tags=['Authentication'])
app.include_router(users.router, tags=['Users'])


@app.get('/')
async def read_root():
    return {'message': 'Working!'}
