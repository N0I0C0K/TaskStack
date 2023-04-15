from data import SessionInfo, TaskInfo, dataManager, as_dict
from utils import logger

from utils.event import Event

from .task_executor import TaskExecutor
from .task_unit import TaskUnit
from .form_model import TaskAddForm

from sqlalchemy import func


class TaskManager:
    def __init__(self) -> None:
        self.task_dict: dict[str, TaskUnit] = dict()
        self.session_dict: dict[str, TaskExecutor] = dict()

        self.task_start_event: Event[TaskExecutor] = Event[TaskExecutor]()
        self.task_finish_event: Event[TaskExecutor] = Event[TaskExecutor]()

        self.load_task()

    def load_task(self):
        with dataManager.session as sess:
            for task in sess.query(TaskInfo).all():
                t_task = TaskUnit(**as_dict(task))
                self.task_dict[task.id] = t_task
                last_exec_time = (
                    sess.query(
                        func.min(SessionInfo.invoke_time)  # pylint: disable=E1102
                    )
                    .filter(SessionInfo.id == task.id)
                    .scalar()
                )
                if last_exec_time is not None:
                    t_task.last_exec_time = last_exec_time

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

        self.task_finish_event.invoke(task_sess)

        logger.debug("%s session unmount and save=> %s", task_sess.id, task_sess)

    def mount_session(self, session: TaskExecutor):
        logger.debug("%s session mount => %s", session.id, session)
        self.session_dict[session.id] = session

        self.task_start_event.invoke(session)

    def del_task(self, task_id: str):
        self.task_dict.pop(task_id)
        with dataManager.session as sess:
            task = sess.query(TaskInfo).filter(TaskInfo.id == task_id).one()
            sess.delete(task)
            sess.commit()

    def get_task(self, task_id: str) -> TaskUnit | None:
        return self.task_dict.get(task_id, None)

    def add_task(self, add_task: TaskAddForm) -> TaskUnit:
        new_task = TaskUnit(
            name=add_task.name,
            command=add_task.command,
            crontab_exp=add_task.crontab_exp,
        )
        self.task_dict[new_task.id] = new_task
        # TODO 检测name是否有重复值
        with dataManager.session as sess:
            task_model = TaskInfo(**new_task.to_dict())
            sess.add(task_model)
            sess.commit()

        if add_task.invoke_once:
            new_task.run()

        return new_task


task_manager = TaskManager()
