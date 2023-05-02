from fastapi import Header, Query, HTTPException, WebSocketException
from auth.auth_manager import auth_manager


async def token_requie(token: str = Header()):
    if not auth_manager.verify_token(token):
        raise HTTPException(502, "invaild token")


async def token_websocket_require(token: str = Query()):
    if not auth_manager.verify_token(token):
        raise WebSocketException(502, "invaild token")
