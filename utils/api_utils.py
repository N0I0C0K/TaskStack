import enum


class HttpState(enum.Enum):
    SUCCESS = 200, "success"
    INVALID_TOKEN = 301, "invalid token"
    UNKONOW_ERR = 500, "unknow error"


def make_response(code: HttpState, data: dict | None = None, **kwargs) -> dict:
    cod, msg = code.value
    if data is not None:
        return {"code": cod, "msg": msg, "data": data, **kwargs}
    else:
        return {"code": cod, "msg": msg, **kwargs}
