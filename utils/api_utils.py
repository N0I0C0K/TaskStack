from pydantic import BaseModel
import enum


class HttpState(enum.Enum):
    SUCCESS = 200, "success"
    FAILED = 400, "failed"
    INVALID_TOKEN = 401, "invalid token"
    CANT_FIND = 404, "can't find"
    UNKONOW_ERR = 500, "unkonow error"


def make_response(
    *,
    code: HttpState = HttpState.SUCCESS,
    data: dict | None = None,
    **kwargs,
) -> dict:
    cod, msg = code.value
    if data is not None:
        return {"code": cod, "msg": msg, "data": data, **kwargs}
    else:
        return {"code": cod, "msg": msg, **kwargs}
