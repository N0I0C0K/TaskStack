from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import Callable
from ..logger import logger


async def websocket_on_recive(websocket: WebSocket, callback: Callable[[dict], None]):
    if websocket.client_state != 1:
        await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            callback(data)

    except WebSocketDisconnect:
        logger.info("websocket disconnect")

    except Exception as e:
        logger.error(e)
        await websocket.close()
