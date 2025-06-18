from contextlib import asynccontextmanager

from fastapi import FastAPI

from simcc.core.database import conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    app.state.last_request_time = None
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/swagger',
)


@app.get('/')
async def read_root():
    return {'message': 'Working!'}
