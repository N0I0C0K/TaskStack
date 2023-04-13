from .logger import logger
from .api_utils import HttpState, make_response

from chardet import detect


def auto_decode(s: bytes) -> str:
    """
    获取`s`对应的解码, 自动判断`s`的编码方式
    """
    if len(s) == 0:
        return ""
    encoding = detect(s)
    return s.decode(encoding["encoding"])
