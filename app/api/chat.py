from fastapi import APIRouter

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat():
    return {"message": "Hello, World!"}
@router.get("/ai")
async def ai():
    return {"message": "Hello, World!"}

