import logging

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_model_manager
from app.model_manager import ModelManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/search',
    tags=['search'],
)


@router.get('/')
async def search(q: str, model_manager: ModelManager = Depends(get_model_manager)):
    try:
        results = await model_manager.search(q)
        return {
            "results": results,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
