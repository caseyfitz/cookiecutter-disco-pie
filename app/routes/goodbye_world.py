from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def goodbye():
    return {"message": "Goodbye World"}
