from .file import config_file_path
from pydantic import BaseSettings
import aiofiles

import json


class AuthConfig(BaseSettings):
    secret: str


class EmailConfig(BaseSettings):
    sender_email: str
    sender_email_password: str
    sender_email_host: str
    receiver_email: str


class AppConfig(BaseSettings):
    auth: AuthConfig
    email_config: EmailConfig


config: AppConfig = None


def load_config():
    global config
    if config_file_path.exists():
        with config_file_path.open() as f:
            config = AppConfig(**json.load(f))
    else:
        raise FileNotFoundError("config file not find!")


def save_config():
    if config is None:
        return
    with config_file_path.open(mode="w") as f:
        json.dump(config.dict(), f, indent=4)


async def save_config_async():
    if config is None:
        return
    async with aiofiles.open(config_file_path, mode="w") as f:
        await f.write(json.dumps(config.dict(), indent=4))


load_config()
