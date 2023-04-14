from fastapi import APIRouter, Depends, HTTPException

from utils.api_base_func import token_requie
from utils.api_utils import make_response, HttpState

from data import dataManager, SessionInfo

from .form_model import TaskAddForm
from .task_session_api import session_api

from .task_manager import task_manager as manager
from .task_unit import TaskUnit

task_api = APIRouter(prefix="/task", dependencies=[Depends(token_requie)])
task_api.include_router(session_api)


async def task_require(task_id: str) -> TaskUnit:
    t = manager.get_task_by_id(task_id)
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


@task_api.delete("/del")
async def del_task(task: TaskUnit = Depends(task_require)):
    pass


@task_api.get("/query")
async def query_task_info(task: TaskUnit = Depends(task_require)):
    return make_response(
        HttpState.SUCCESS,
        task=task.to_dict(),
    )


@task_api.post("/queryHistory")
async def query_task_history(task: TaskUnit = Depends(task_require)):
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
