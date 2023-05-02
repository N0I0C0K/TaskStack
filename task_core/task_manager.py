from data import SessionInfo, TaskInfo, dataManager, as_dict
from utils import logger, formate_time
from utils.file import output_store_path

from utils.event import Event
from utils.thread_pool import thread_pool

from .task_executor import TaskExecutor
from .task_unit import TaskUnit
from .form_model import TaskAddForm

from sqlalchemy import func


class CantDelTask(Exception):
    pass


class TaskStillRunning(Exception):
    pass


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
                t_task = TaskUnit(
                    id=task.id,  # type: ignore
                    name=task.name,  # type: ignore
                    command=task.command,  # type: ignore
                    active=task.active,  # type: ignore
                    create_time=task.create_time,  # type: ignore
                    crontab_exp=task.crontab_exp,  # type: ignore
                )
                self.task_dict[task.id] = t_task  # type: ignore
                last_exec_time = (
                    sess.query(
                        func.min(SessionInfo.start_time)  # pylint: disable=E1102
                    )
                    .filter(SessionInfo.id == task.id)
                    .scalar()
                )
                if last_exec_time is not None:
                    t_task.last_exec_time = last_exec_time

    def unmount_save_session(self, sessionid: str):
        task_sess = self.session_dict.pop(sessionid)

        if task_sess.running:
            raise TaskStillRunning

        with dataManager.session as sess:
            data_sess = (
                sess.query(SessionInfo).filter(SessionInfo.id == task_sess.id).one()
            )
            data_sess.finish_time = task_sess.finish_time
            data_sess.success = task_sess.success
            sess.commit()

        self.task_finish_event.invoke(task_sess)

        out_file = output_store_path / f"{task_sess.id}.out"
        out_file.touch()

        with out_file.open("w+", encoding="utf-8") as file:
            file.write(task_sess.info)
            file.write(task_sess.stdout)
        logger.debug("save the out put to %s", out_file.as_posix())
        logger.debug("%s session unmount and save=> %s", task_sess.id, task_sess)

    def mount_session(self, session: TaskExecutor):
        logger.debug("%s session mount => %s", session.id, session.command)
        self.session_dict[session.id] = session

        with dataManager.session as sess:
            data_sess = SessionInfo(
                id=session.id,
                start_time=session.start_time,
                finish_time=session.finish_time,
                task_id=session.task_id,
                command=session.raw_command,
            )
            sess.add(data_sess)
            sess.commit()

        self.task_start_event.invoke(session)

    def del_task(self, task_id: str):
        if self.task_dict[task_id].running:
            raise CantDelTask("task is still running")
        self.task_dict.pop(task_id)
        with dataManager.session as sess:
            task = sess.query(TaskInfo).filter(TaskInfo.id == task_id).one()
            sess.delete(task)
            sess.commit()

    def get_task(self, task_id: str) -> TaskUnit | None:
        return self.task_dict.get(task_id, None)

    def get_exector(self, session_id: str) -> TaskExecutor | None:
        return self.session_dict.get(session_id, None)

    def add_task(self, add_task: TaskAddForm) -> TaskUnit:
        new_task = TaskUnit(
            name=add_task.name,
            command=add_task.command,
            crontab_exp=add_task.crontab_exp,
        )
        self.task_dict[new_task.id] = new_task

        # TODO 检测name是否有重复值
        with dataManager.session as sess:
            task_model = TaskInfo(**new_task.__dict__)
            sess.add(task_model)
            sess.commit()

        if add_task.invoke_once:
            new_task.run()

        return new_task


task_manager = TaskManager()
