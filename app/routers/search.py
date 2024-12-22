from fastapi import APIRouter

router = APIRouter(
    prefix='/search',
    tags=['search'],
)


@router.get('/')
async def search(q: str):
    # TODO: implement the search logic
    return {'q': q}
