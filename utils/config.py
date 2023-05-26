from .file import config_file_path
from pydantic import BaseSettings
import yaml


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
if config_file_path.exists():
    with config_file_path.open() as f:
        config = AppConfig(**yaml.safe_load(f))
else:
    raise FileNotFoundError("config file not find!")
