FROM python:3.13-slim-bookworm
WORKDIR /app

RUN pip install poetry

ENV FLASK_APP=src.priority
WORKDIR /usr/app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY ./src ./src

EXPOSE 8000
CMD ["poetry", "run", "gunicorn", "--reload", "--bind", "0.0.0.0:8000", "src.priority:app"]
