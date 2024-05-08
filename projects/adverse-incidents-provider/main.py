from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException

from app.middleware.api_key_middleware import api_key_middleware
from app.routes import adverse_incidents_provider_routes

app = FastAPI()

app.include_router(adverse_incidents_provider_routes.router)


@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    if request.url.path != "/ping":
        try:
            request = await api_key_middleware(request)
        except HTTPException:
            return JSONResponse(status_code=403, content={"message": "Wrong API Key"})
    return await call_next(request)


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
    return {"message": "Adverse Incidents Provider Service"}
