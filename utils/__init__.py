from .logger import logger
from .api_utils import HttpState, make_response
from .time_func import formate_time

from chardet import detect
from secrets import token_hex


def auto_decode(s: bytes) -> str:
    """
    获取`s`对应的解码, 自动判断`s`的编码方式
    """
    if len(s) == 0:
        return ""
    encoding = detect(s)
    return s.decode(encoding["encoding"])


def uuid():
    return token_hex(16)
