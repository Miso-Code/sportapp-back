ARG PY_VERSION="3.12-slim"

FROM python:${PY_VERSION}

COPY pyproject.toml poetry.lock main.py /service/

COPY app/ /service/app/

WORKDIR /service

RUN pip install poetry && poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "2"]
