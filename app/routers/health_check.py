from fastapi import APIRouter

router = APIRouter()


@router.get('/', tags=['health check'])
async def health_check():
    return {'message': 'OK!'}
