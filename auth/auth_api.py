from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi import Depends

from .auth_manager import auth_manager
from utils import HttpState, make_response
from utils.api_base_func import token_requie
import time

auth_api = APIRouter(prefix="/auth")


@auth_api.get("/login")
async def login(secret_key: str):
    token = auth_manager.auth_secret_key(secret_key)
    if token is None:
        return make_response(code=HttpState.INVALID_TOKEN)
    else:
        j_res = JSONResponse(
            content=make_response(token=token.token, active_time=token.active_time)
        )
        j_res.set_cookie("token", token.token)
        return j_res


@auth_api.get("/beat")
async def beat(token=Depends(token_requie)):
    return make_response()


@auth_api.get("/sys_time")
async def get_system_time():
    return {"time": time.time()}
