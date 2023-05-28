from fastapi import APIRouter, Depends, WebSocket
from pydantic import BaseModel
import asyncio

from utils import logger
from utils.api_base_func import token_requie, token_websocket_require
from utils.api_utils import make_response
from utils.config import config, save_config_async

from .user_center import user_center

user_api = APIRouter(prefix="/user", dependencies=[Depends(token_requie)])


@user_api.get("/email/config")
async def get_email_config():
    return make_response(
        sender_email=config.email_config.sender_email,
        sender_password=config.email_config.sender_email_password,
        smtp_server=config.email_config.sender_email_host,
        receiver_email=config.email_config.receiver_email,
    )


class EmailConfig(BaseModel):
    sender_email: str
    sender_password: str
    smtp_server: str
    receiver_email: str


@user_api.post("/email/config")
async def set_email_config(email_config: EmailConfig):
    config.email_config.sender_email = email_config.sender_email
    config.email_config.sender_email_password = email_config.sender_password
    config.email_config.sender_email_host = email_config.smtp_server
    config.email_config.receiver_email = email_config.receiver_email
    await save_config_async()
    return make_response()


@user_api.get("/system/info")
async def get_system_info():
    return make_response(
        data=user_center.system_info.get_info(),
    )


@user_api.websocket("/event/listen")
async def task_event_listener(
    websocket: WebSocket, token=Depends(token_websocket_require)
):
    await websocket.accept()

    from fastapi.websockets import WebSocketDisconnect, WebSocketState

    from task_core.task_executor import TaskExecutor
    from task_core.task_manager import task_manager as manager

    print("link to listener")

    async def task_start(exector: TaskExecutor):
        await websocket.send_json(
            {
                "event": "task_start",
                "data": {
                    "session_id": exector.id,
                    "task_id": exector.task_id,
                },
            }
        )

    async def task_finish(exector: TaskExecutor):
        await websocket.send_json(
            {
                "event": "task_finish",
                "data": {
                    "session_id": exector.id,
                    "task_id": exector.task_id,
                },
            }
        )

    async def system_info_update():
        while websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_json(
                {
                    "event": "system_info_update",
                    "data": user_center.system_info.get_info(),
                }
            )
            await asyncio.sleep(1)

    loop = asyncio.get_running_loop()

    try:
        manager.task_start_event += task_start
        manager.task_finish_event += task_finish
        loop.create_task(system_info_update())

        while websocket.client_state == WebSocketState.CONNECTED:
            s = await websocket.receive_text()
            if s == "disconnect":
                break
        await websocket.close()

    except WebSocketDisconnect:
        pass
    finally:
        logger.debug("disconnect listener")
        manager.task_start_event -= task_start
        manager.task_finish_event -= task_finish
