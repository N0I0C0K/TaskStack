import time
import secrets
from utils.config import config
from dataclasses import dataclass, field

Token = str


@dataclass
class TokenSession:
    secret_key: str
    token: str
    active_time: float = field(default_factory=time.time)


class AuthManager:
    def __init__(self) -> None:
        self.token_dic: dict[Token, TokenSession] = dict()

    def auth_secret_key(self, key: str) -> TokenSession | None:
        tar = time.strftime(config.auth.secret, time.localtime())
        if tar == key:
            token = secrets.token_hex(16)
            token_session = TokenSession(key, token)
            self.token_dic[token] = token_session
            return token_session
        return None

    def verify_token(self, token: str) -> bool:
        return token in self.token_dic


auth_manager = AuthManager()
