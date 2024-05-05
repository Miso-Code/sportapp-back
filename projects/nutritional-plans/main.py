from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes import nutritional_plans_routes
from app.exceptions.exceptions import NotFoundError
from app.models.model import base
from app.config.db import engine

app = FastAPI()

base.metadata.reflect(bind=engine)
base.metadata.create_all(bind=engine)

app.include_router(nutritional_plans_routes.router)


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=404, content={"message": str(exc)})


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


@app.get("/ping")
async def root():
    return {"message": "Nutritional Plans Service"}
