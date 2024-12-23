import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.model_manager import ModelManager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading models...")

    model_manager = ModelManager()
    await model_manager.load_models()
    await model_manager.load_dataset()

    app.state.model_manager = model_manager

    logger.info("Models loaded successfully")

    yield

    logger.info("Cleaning up...")
    await app.state.model_manager.cleanup()
