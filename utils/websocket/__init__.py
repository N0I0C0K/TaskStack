from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import Callable
from ..logger import logger
import json


async def websocket_on_recive(websocket: WebSocket, callback: Callable[[dict], None]):
    if websocket.client_state.value != 1:
        await websocket.accept()
    print("websocket_on_recive")
    try:
        while True:
            data = await websocket.receive_text()
            callback(json.loads(data))

    except WebSocketDisconnect:
        logger.info("websocket disconnect")

    except Exception as e:
        logger.error(e)
        await websocket.close()
