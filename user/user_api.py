from fastapi import APIRouter, Depends
from utils.api_utils import make_response
from utils.api_base_func import token_requie
from utils.config import config, save_config_async
from pydantic import BaseModel

user_api = APIRouter(prefix="/user", dependencies=[Depends(token_requie)])


@user_api.get("/email/config")
async def get_email_config():
    return make_response(
        sender_email=config.email_config.sender_email,
        sender_password=config.email_config.sender_email_password,
        smtp_server=config.email_config.sender_email_host,
        receiver_email=config.email_config.receiver_email,
    )


class EmailConfig(BaseModel):
    sender_email: str
    sender_password: str
    smtp_server: str
    receiver_email: str


@user_api.post("/email/config")
async def set_email_config(email_config: EmailConfig):
    config.email_config.sender_email = email_config.sender_email
    config.email_config.sender_email_password = email_config.sender_password
    config.email_config.sender_email_host = email_config.smtp_server
    config.email_config.receiver_email = email_config.receiver_email
    await save_config_async()
    return make_response()
