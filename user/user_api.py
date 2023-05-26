from fastapi import APIRouter, Depends
from utils.api_utils import make_response
from utils.api_base_func import token_requie
from utils.config import config

user_api = APIRouter(prefix="/user", dependencies=[Depends(token_requie)])


@user_api.get("/email/config")
async def get_email_config():
    return make_response(config.email_config)
