from fastapi import Header, Cookie, HTTPException
from auth.auth_manager import auth_manager


async def token_requie(token: str = Header()):
    if not auth_manager.verify_token(token):
        raise HTTPException(502, "invaild token")
