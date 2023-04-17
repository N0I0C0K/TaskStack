import time

from utils.api_utils import make_response, HttpState
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from data import SessionInfo, dataManager, as_dict
from utils.api_base_func import token_requie

from sqlalchemy.orm import Query

from utils.file import output_store_path


class SessionQuery(BaseModel):
    starttime: float | None
    endtime: float | None

    task_id: list[str] | None


session_api = APIRouter(prefix="/session", dependencies=[Depends(token_requie)])


@session_api.get("/find")
async def find_session(form: SessionQuery):
    res: list[SessionInfo] = []
    with dataManager.session as sess:
        query_exp: Query = None
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
                SessionInfo.invoke_time > form.starttime,
                SessionInfo.finish_time <= form.endtime,
            ).all()
        )
    return make_response(session=[as_dict(x) for x in res])


@session_api.get("/get")
async def get_session_detail(session_id: str):
    with dataManager.session as sess:
        sess_tar = sess.query(SessionInfo).filter(SessionInfo.id == session_id).first()
        if sess_tar is None:
            return make_response(HttpState.CANT_FIND)
        out_file = output_store_path / f"{sess_tar.id}.out"
        out_text = "out put missing" if not out_file.exists() else out_file.read_text()
        return make_response(**as_dict(sess_tar), output=out_text)
