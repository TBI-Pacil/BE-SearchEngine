from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # TODO: Load the ML model
    yield
    # TODO: Clean up the ML models and release the resources if necessary
