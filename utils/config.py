from .file import config_file_path
from pydantic import BaseSettings
import yaml


class AuthConfig(BaseSettings):
    secret: str


class AppConfig(BaseSettings):
    auth: AuthConfig


config: AppConfig = None
if config_file_path.exists():
    with config_file_path.open() as f:
        config = AppConfig(**yaml.safe_load(f))
else:
    raise FileNotFoundError("config file not find!")
