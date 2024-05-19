import logging
from threading import Thread

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import ExternalServiceError
from app.tasks.processor import Processor

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processor = Processor(logger)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting processing incidents...")
    thread = Thread(target=processor.process_incidents)
    thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping processing incidents...")
    processor.stop_processing()


@app.exception_handler(ExternalServiceError)
async def not_found_error_handler(request, exc):
    return JSONResponse(status_code=500, content={"message": str(exc)})


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
    return {"message": "Alerts Service"}
