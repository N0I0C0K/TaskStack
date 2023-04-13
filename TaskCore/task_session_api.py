from fastapi import APIRouter

session_api = APIRouter(prefix="/session")


@session_api.post("/find")
async def find_session():
    pass
