import time
import secrets
from utils import formate_time


# external visit class for session, use unique id to visit session, external_id -> session_id, create_time -> this class create time, duration->this external id duration
# session_id -> session target
class ExternalVisit:
    def __init__(
        self,
        session_id: str,
        external_id: str = "",
        duration: float = 60 * 60,
    ) -> None:
        self.session_id = session_id
        self.external_id = (
            external_id
            if external_id and len(external_id) > 0
            else secrets.token_urlsafe(32)
        )
        self.create_time = time.time()
        self.duration = duration
        self.expire_time = formate_time(self.create_time + self.duration)
        self.link = f"/external_session/info?external_id={self.external_id}"

    def vaild(self) -> bool:
        return time.time() - self.create_time <= self.duration


# external visit manager, manage all external visit
class ExternalVisitManager:
    def __init__(self) -> None:
        self.external_visit_dict: dict[str, ExternalVisit] = dict()

    def add_external_visit(self, session_id: str) -> ExternalVisit:
        external_visit = ExternalVisit(session_id)
        self.external_visit_dict[external_visit.external_id] = external_visit

        return external_visit

    def get_external_visit(self, external_id: str) -> ExternalVisit | None:
        return self.external_visit_dict.get(external_id, None)

    def del_external_visit(self, external_id: str):
        self.external_visit_dict.pop(external_id, None)

    def check_external_visit(self, external_id: str) -> bool:
        external_visit = self.get_external_visit(external_id)
        if external_visit is None:
            return False
        if not external_visit.vaild():
            self.del_external_visit(external_id)
            return False
        return True


external_visit_manager = ExternalVisitManager()
