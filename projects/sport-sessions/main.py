from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routes import sport_sessions
from app.exceptions.exceptions import NotFoundError, NotActiveError, InvalidApiKeyError
from app.models.model import base
from app.config.db import engine

app = FastAPI()

base.metadata.create_all(bind=engine)

app.include_router(sport_sessions.router)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(NotActiveError)
async def not_active_error_handler(request, exc):
    return JSONResponse(status_code=423, content={"message": str(exc)})


@app.exception_handler(InvalidApiKeyError)
async def invalid_api_key_error_handler(request, exc):
    return JSONResponse(status_code=403, content={"message": str(exc)})


@app.get("/ping")
async def root():
    return {"message": "Sport Sessions Service"}
