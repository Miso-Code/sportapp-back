import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import users_routes
from app.exceptions.exceptions import NotFoundError, InvalidValueError
from app.config.db import engine, base, session_local
from app.tasks.sync_db import sync_users
from app.utils.utils import sleep

load_dotenv()
app = FastAPI()

base.metadata.create_all(bind=engine)

app.include_router(users_routes.router)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(sync_users(db=session_local(), sleep=sleep))


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(InvalidValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.get("/ping")
async def root():
    return {"message": "Users Service"}
