import time
import secrets
from utils.config import config
from dataclasses import dataclass, field

from utils.thread_pool import main_loop

import asyncio

Token = str


@dataclass
class TokenSession:
    secret_key: str
    token: str
    active_time: float = field(default_factory=time.time)
    end_time: int = field(init=False, default=60 * 60 * 24)

    def __hash__(self) -> int:
        return hash(self.token)

    def beat(self):
        self.active_time = time.time()

    @property
    def available(self):
        return time.time() - self.active_time < self.end_time


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

    def beat(self, token: str):
        if token in self.token_dic:
            self.token_dic[token].beat()

    def verify_token(self, token: str) -> bool:
        if token not in self.token_dic:
            return False
        token_sess = self.token_dic[token]
        if not token_sess.available:
            self.token_dic.pop(token)
            return False
        token_sess.beat()
        return True


auth_manager = AuthManager()
