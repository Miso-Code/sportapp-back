from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.db import engine, base
from app.exceptions.exceptions import NotFoundError, InvalidValueError, InvalidCredentialsError, EntityExistsError
from app.routes import training_plan_routes

app = FastAPI()

base.metadata.reflect(bind=engine)
base.metadata.create_all(bind=engine)

app.include_router(training_plan_routes.router)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


@app.exception_handler(InvalidValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": str(exc)})


@app.exception_handler(EntityExistsError)
async def entity_exists_error_handler(request, exc):
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
    return {"message": "Training Plans Service"}
