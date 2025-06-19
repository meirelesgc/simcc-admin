from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from simcc.core.database import conn
from simcc.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await conn.connect()
    yield
    await conn.disconnect()


app = FastAPI(
    lifespan=lifespan,
    docs_url='/swagger',
)

app.include_router(users.router, tags=['arrange'])
app.include_router(auth.router, prefix='/auth', tags=['Authentication'])


@app.get('/', response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - SIMCC</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background-color: #f0f2f5;
            }
            .login-container {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
            }
            .orcid-button {
                display: inline-flex;
                align-items: center;
                padding: 12px 24px;
                border-radius: 20px;
                background-color: #a6ce39;
                color: white;
                text-decoration: none;
                font-weight: bold;
                font-size: 16px;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .orcid-button:hover {
                background-color: #89ac2d;
            }
            .orcid-button img {
                width: 24px;
                height: 24px;
                margin-right: 12px;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h1>Bem-vindo ao SIMCC</h1>
            <p>Sistema Integrado de Monitoramento de Culturas de Cacao</p>
            <a href="https://simcc.uesc.br/admin/auth/orcid/login" class="orcid-button">
                <img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_24x24.png" alt="ORCID logo">
                <span>Entrar com ORCID</span>
            </a>
        </div>
    </body>
    </html>
    """
