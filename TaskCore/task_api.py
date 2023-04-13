from fastapi import APIRouter, Depends

from utils.api_base_func import token_requie

from .form_model import TaskAddForm
from .task_session_api import session_api

task_api = APIRouter(prefix="/task", dependencies=[Depends(token_requie)])
task_api.include_router(session_api)


@task_api.post("/new")
async def new_task(form: TaskAddForm):
    pass


@task_api.post("/del")
async def del_task():
    pass


@task_api.post("/query")
async def query_task_info():
    pass


@task_api.post("/queryHistory")
async def query_task_history():
    pass
