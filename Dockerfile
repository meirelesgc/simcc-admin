FROM python:3.12.10-alpine3.20

ENV POETRY_VIRTUALENVS_CREATE=false

RUN apk update && apk upgrade && apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers

WORKDIR /app

COPY . .

RUN pip install poetry && \
    poetry config installer.max-workers 10 && \
    poetry install --no-interaction --no-ansi

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "adm_simcc.app:create_app()"]
