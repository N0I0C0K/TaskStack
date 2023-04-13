from fastapi import APIRouter, Depends
from utils.api_base_func import token_requie

session_api = APIRouter(prefix="/session", dependencies=[Depends(token_requie)])


@session_api.post("/find")
async def find_session():
    pass
