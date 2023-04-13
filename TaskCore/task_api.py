from fastapi import APIRouter

task_api = APIRouter(prefix="/task")


@task_api.post("/new")
async def new_task():
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
