from fastapi.routing import APIRouter
from pydantic import BaseModel

from .auth_manager import auth_manager
from utils import HttpState, make_response
import time

auth_api = APIRouter(prefix="/auth")


class LoginForm(BaseModel):
    secret_key: str


@auth_api.post("/login")
async def login(form: LoginForm):
    token = auth_manager.auth_secret_key(form.secret_key)
    if token is None:
        return make_response(HttpState.UNKONOW_ERR)
    else:
        return make_response(
            HttpState.SUCCESS, token=token.token, active_time=token.active_time
        )


@auth_api.get("/sys_time")
async def get_system_time():
    return {"time": time.time()}
