from pydantic import BaseModel
import enum


class HttpState(enum.Enum):
    SUCCESS = 200, "success"
    INVALID_TOKEN = 501, "invalid token"
    CANT_FIND = 502, "can not find what you want to find"
    UNKONOW_ERR = 600, "unknow error"


def make_response(
    code: HttpState = HttpState.SUCCESS,
    data: dict | None = None,
    **kwargs,
) -> dict:
    cod, msg = code.value
    if data is not None:
        return {"code": cod, "msg": msg, "data": data, **kwargs}
    else:
        return {"code": cod, "msg": msg, **kwargs}
