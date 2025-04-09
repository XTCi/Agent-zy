from fastapi import APIRouter

router = APIRouter(tags=["agent"])

@router.post("/agent")
async def agent():
    return {"message": "Hello, World!"}


