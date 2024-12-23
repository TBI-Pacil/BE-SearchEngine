from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.index import initialize_data

from .config import settings
from .context import lifespan
from .routers import health_check, search

app = FastAPI(lifespan=lifespan)

initialize_data()

api_v1 = APIRouter(prefix='/api/v1')

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_check.router)

api_v1.include_router(search.router)

app.include_router(api_v1)
