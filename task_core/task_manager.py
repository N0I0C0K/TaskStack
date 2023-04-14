from data import SessionInfo, TaskInfo, dataManager, as_dict
from utils import logger


from .task_executor import TaskExecutor
from .task_unit import TaskUnit
from .form_model import TaskAddForm


class TaskManager:
    def __init__(self) -> None:
        self.task_dict: dict[str, TaskUnit] = dict()
        self.session_dict: dict[str, TaskExecutor] = dict()
        self.load_task()

    def load_task(self):
        with dataManager.session as sess:
            for task in sess.query(TaskInfo).all():
                self.task_dict[task.id] = TaskUnit(**as_dict(task))

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

    def add_task(self, add_task: TaskAddForm) -> TaskUnit:
        new_task = TaskUnit(
            name=add_task.name,
            command=add_task.command,
        )
        self.task_dict[new_task.id] = new_task
        # TODO 检测name是否有重复值
        with dataManager.session as sess:
            task_model = TaskInfo(**new_task.to_dict())
            sess.add(task_model)
            sess.commit()
        return new_task

    def get_task_by_id(self, task_id: str) -> TaskUnit | None:
        return self.task_dict.get(task_id, None)


task_manager = TaskManager()
