ARG PY_VERSION="3.12-slim"

FROM python:${PY_VERSION}

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--workers", "2"]
