from fastapi import APIRouter
from data import SessionInfo, TaskInfo, dataManager
from .task_external_manager import external_visit_manager
from utils.api_utils import make_response, HttpState
from .task_executor import get_session_output_from_file

task_external_api = APIRouter(prefix="/external_session")


@task_external_api.get("/info")
async def get_external_task_info(external_id: str):
    """
    get external session info(SessionInfo)
    """
    if not external_visit_manager.check_external_visit(external_id):
        return make_response(code=HttpState.FAILED, msg="external id not exist")
    external_visit = external_visit_manager.get_external_visit(external_id)

    with dataManager.session as sess:
        session_info = (
            sess.query(SessionInfo)
            .filter(SessionInfo.id == external_visit.session_id)
            .first()
        )
        if session_info is None:
            return make_response(code=HttpState.FAILED, msg="session not exist")
        return make_response(
            code=HttpState.SUCCESS,
            data=session_info.to_dict(),
            output=get_session_output_from_file(session_info.id),
        )
