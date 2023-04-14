from data import SessionInfo, TaskInfo, dataManager
from utils import logger

from .task_executor import TaskExecutor
from .task_unit import TaskUnit


class TaskManager:
    def __init__(self) -> None:
        self.task_dict: dict[str, TaskUnit] = dict()
        self.session_dict: dict[str, TaskExecutor] = dict()

    def load_task(self):
        with dataManager.session as sess:
            for task in sess.query(TaskInfo).all():
                self.task_dict[task.id] = TaskUnit(
                    task.id,
                    task.name,
                    task.active,
                    task.create_time,
                    task.command,
                    task.crontab_exp,
                )

    def unmount_save_session(self, sessionid: str):
        task_sess = self.session_dict.pop(sessionid)
        with dataManager.session as sess:
            data_sess = SessionInfo(
                id=task_sess.id,
                invoke_time=task_sess.start_time,
                finish_time=task_sess.finish_time,
                task_id=task_sess.task_id,
                command=task_sess.raw_command,
            )
            sess.add(data_sess)
            sess.commit()
        logger.debug("%s session unmount and save=> %s", task_sess.id, task_sess)

    def mount_session(self, session: TaskExecutor):
        logger.debug("%s session mount => %s", session.id, session)
        self.session_dict[session.id] = session

    def add_task(self) -> str:
        pass


task_manager = TaskManager()
