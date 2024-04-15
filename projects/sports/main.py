from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routes import sports
from app.exceptions.exceptions import NotFoundError
from app.models.model import base
from app.config.db import engine

app = FastAPI()

base.metadata.create_all(bind=engine)

app.include_router(sports.router)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.get("/ping")
async def root():
    return {"message": "Sports Service"}
