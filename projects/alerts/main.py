import json
import logging
from threading import Thread

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.settings import Config
from app.routes import alerts_routes
from app.exceptions.exceptions import NotFoundError
from app.models.model import base
from app.config.db import engine
from app.tasks.prioritizer import QueueProcessor
from app.wrapper.firebase_wrapper import FirebaseWrapper

app = FastAPI()
firebase_wrapper = FirebaseWrapper()

firebase_wrapper.initialize_app(firebase_wrapper.generate_credentials())

base.metadata.reflect(bind=engine)
base.metadata.create_all(bind=engine)

app.include_router(alerts_routes.router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

queue_processor = QueueProcessor()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting processing queues thread")
    thread = Thread(target=queue_processor.process_queues)
    thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    queue_processor.stop_processing()


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
    return {"message": "Alerts Service"}
