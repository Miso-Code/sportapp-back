import asyncio

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import users_routes
from app.exceptions.exceptions import NotFoundError, InvalidValueError, InvalidCredentialsError, EntityExistsError, PlanPaymentError
from app.config.db import engine, base, session_local
from app.tasks.sync_db import sync_users
from app.utils.utils import async_sleep

load_dotenv()
app = FastAPI()

base.metadata.reflect(bind=engine)
base.metadata.create_all(bind=engine)

app.include_router(users_routes.router)


@app.on_event("startup")
async def startup_event():
    try:
        asyncio.create_task(sync_users(db=session_local(), sleep=async_sleep))
    except Exception as e:
        print(f"Error creating task: {e}")
        raise e


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(InvalidValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(EntityExistsError)
async def entity_exists_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(PlanPaymentError)
async def plan_payment_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    validations = exc.errors()
    errors = []
    for validation in validations:
        errors.append(
            {
                "loc": validation["loc"],
                "msg": validation["msg"],
            },
        )

    return JSONResponse(status_code=400, content={"message": {"errors": errors}})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_error_handler(request, exc):
    return JSONResponse(status_code=401, content={"message": str(exc)})


@app.get("/ping")
async def root():
    return {"message": "Users Service"}
