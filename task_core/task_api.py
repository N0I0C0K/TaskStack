from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from data import SessionInfo, dataManager
from utils.api_base_func import token_requie, token_websocket_require
from utils.api_utils import HttpState, make_response
from task_core.task_executor import TaskExecutor
from utils import logger

from .form_model import TaskAddForm, TaskModifyForm, TaskRunForm
from .task_manager import task_manager as manager
from .task_session_api import session_api
from .task_unit import TaskUnit


task_api = APIRouter(prefix="/task", dependencies=[Depends(token_requie)])
task_api.include_router(session_api)


async def task_id_require(task_id: str) -> TaskUnit:
    t = manager.get_task(task_id)
    if t is None:
        raise HTTPException(501, "task_id is invaild")
    return t


@task_api.post("/create")
async def new_task(form: TaskAddForm):
    task = manager.add_task(form)
    return make_response(
        HttpState.SUCCESS,
        task=task.to_dict(),
    )


@task_api.get("/list")
async def get_all_task():
    return make_response(
        HttpState.SUCCESS,
        list=list(
            map(
                lambda x: x.to_dict(),
                manager.task_dict.values(),
            )
        ),
    )


@task_api.post("/modify")
async def modify_task(
    form: TaskModifyForm,
    task: TaskUnit = Depends(task_id_require),
):
    unit = manager.modify_task(task.id, form)
    return make_response(HttpState.SUCCESS, task=unit.to_dict())


@task_api.put("/active")
async def set_task_active(
    active: bool,
    task: TaskUnit = Depends(task_id_require),
):
    task.set_active(active)
    return make_response(HttpState.SUCCESS)


@task_api.delete("/del")
async def del_task(task: TaskUnit = Depends(task_id_require)):
    manager.del_task(task.id)
    return make_response(HttpState.SUCCESS)


@task_api.get("/query")
async def query_task_info(task: TaskUnit = Depends(task_id_require)):
    return make_response(
        HttpState.SUCCESS,
        task=task.to_dict(),
    )


@task_api.get("/history")
async def query_task_history(task: TaskUnit = Depends(task_id_require)):
    with dataManager.session as sess:
        task_sess = (
            sess.query(SessionInfo)
            .filter(
                SessionInfo.task_id == task.id,
            )
            .all()
        )
        return make_response(
            HttpState.SUCCESS,
            sessions=[x.to_dict() for x in task_sess],
        )


@task_api.get("/run")
async def run_task(task: TaskUnit = Depends(task_id_require)):
    return make_response(session_id=task.run())


@task_api.post("/run_with_input")
async def run_task_with_input(
    form: TaskRunForm,
    task: TaskUnit = Depends(task_id_require),
):
    return make_response(session_id=task.run(form.command_input))


@task_api.get("/stop")
async def stop_task(task: TaskUnit = Depends(task_id_require)):
    return make_response(success=(await task.stop()))


@task_api.websocket("/listener")
async def task_event_listener(
    websocket: WebSocket, token=Depends(token_websocket_require)
):
    await websocket.accept()

    print("link to listener")

    async def task_start(exector: TaskExecutor):
        logger.debug(
            "[Send] tarsk start , session id: %s, task id: %s",
            exector.id,
            exector.task_id,
        )
        await websocket.send_json(
            {
                "event": "task_start",
                "session_id": exector.id,
                "task_id": exector.task_id,
            }
        )

    async def task_finish(exector: TaskExecutor):
        logger.debug(
            "[Send]  task finish , session id: %s, task id: %s",
            exector.id,
            exector.task_id,
        )
        await websocket.send_json(
            {
                "event": "task_finish",
                "session_id": exector.id,
                "task_id": exector.task_id,
            }
        )

    try:
        manager.task_start_event += task_start
        manager.task_finish_event += task_finish

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
