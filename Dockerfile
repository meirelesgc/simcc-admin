FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Copia apenas arquivos necessários
COPY . .

# Instala o Poetry e as dependências
RUN pip install poetry && \
    poetry config installer.max-workers 10 && \
    poetry install --no-interaction --no-ansi

# Expondo a porta da aplicação
EXPOSE 8080

# Comando padrão para inicializar
CMD ["gunicorn", "-b", "0.0.0.0:8080", "adm_simcc:create_app()", "--reload", "--log-level", "info", "--access-logfile", "files/access.log", "--error-logfile", "files/error.log", "--workers", "4"]
