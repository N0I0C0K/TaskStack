import asyncio
import time

import aiofiles
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Query

from task_core.task_manager import task_manager
from data import SessionInfo, dataManager
from utils.api_base_func import token_requie
from utils.api_utils import HttpState, make_response
from utils.file import output_store_path


class SessionQuery(BaseModel):
    starttime: float | None
    endtime: float | None

    task_id: list[str] | None


session_api = APIRouter(prefix="/session", dependencies=[Depends(token_requie)])


@session_api.get("/all")
async def get_all_session(start: int, num: int):
    with dataManager.session as sess:
        all_seg = sess.query(SessionInfo)
        sessions = all_seg.offset(start).limit(num).all()

        return make_response(
            all_nums=all_seg.count(), sessions=[ts.to_dict() for ts in sessions]
        )


@session_api.get("/find")
async def find_session(form: SessionQuery):
    """
    寻找给定时间区间内给定taskid的任务
    """
    res: list[SessionInfo] = []
    with dataManager.session as sess:
        query_exp: Query
        if form.task_id is not None:
            query_exp = sess.query(SessionInfo).filter(
                SessionInfo.task_id.in_(form.task_id)
            )
        else:
            query_exp = sess.query(SessionInfo)
        if form.starttime is None:
            form.starttime = 0
        if form.endtime is None:
            form.endtime = time.time()
        res.extend(
            query_exp.filter(
                SessionInfo.start_time > form.starttime,
                SessionInfo.finish_time <= form.endtime,
            ).all()
        )
    return make_response(session=[x.to_dict() for x in res])


@session_api.get("/output")
async def get_session_output(session_id: str):
    with dataManager.session as sess:
        sess_tar = sess.query(SessionInfo).filter(SessionInfo.id == session_id).first()
        if sess_tar is None:
            return make_response(code=HttpState.CANT_FIND)
        out_text = "output missing"
        if sess_tar.running:
            exector = task_manager.get_exector(session_id)
            if exector is not None:
                out_text = exector.stdout
        else:
            out_file = output_store_path / f"{sess_tar.id}.out"
            if out_file.exists():
                async with aiofiles.open(out_file.as_posix()) as file:
                    out_text = await file.read()
        return make_response(
            session_id=session_id, finish=sess_tar.finish, output=out_text
        )


@session_api.get("/info")
async def get_sesion_info(session_id: str):
    with dataManager.session as sess:
        sess_tar = sess.query(SessionInfo).filter(SessionInfo.id == session_id).first()
        if sess_tar is None:
            return make_response(code=HttpState.CANT_FIND)
        return make_response(session=sess_tar.to_dict())


@session_api.get("/stop")
async def stop_session(session_id: str):
    exector = task_manager.get_exector(session_id)
    if exector is None:
        return make_response(code=HttpState.CANT_FIND)
    await exector.kill()
    return make_response()


@session_api.websocket("/communicate")
async def session_communicate(session_id: str, *, socket: WebSocket):
    task_exector = task_manager.get_exector(session_id)

    if task_exector is None:
        await socket.close()
        return

    await socket.accept()
    try:
        await socket.receive_text()
        while True:
            output_line = await task_exector.readline()
            await socket.send_text(output_line)
            if task_exector.finished:
                break
        await socket.send_text(f"task-{session_id} over")
    except WebSocketDisconnect:
        pass
    else:
        await socket.close()
