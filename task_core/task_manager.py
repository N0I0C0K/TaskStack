from data import SessionInfo, TaskInfo, dataManager
from utils import logger
from utils.file import output_store_path

from utils.event import Event

from .task_executor import TaskExecutor
from .task_unit import TaskUnit
from .form_model import TaskAddForm, TaskModifyForm

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
        self.task_error_event: Event[TaskExecutor] = Event[TaskExecutor]()

        self.load_task()
        self.handle_last_unfinish_session()

    def handle_last_unfinish_session(self):
        """
        handel unexpect exit process session during last run.
        """
        with dataManager.session as sess:
            error_session = (
                sess.query(SessionInfo)
                .filter(SessionInfo.finish_time < SessionInfo.start_time)
                .all()
            )
            for es in error_session:
                es.finish_time = es.start_time
                es.success = False
            sess.commit()

    def load_task(self):
        with dataManager.session as sess:
            for task in sess.query(TaskInfo).all():
                t_task = TaskUnit(
                    id=task.id,
                    name=task.name,
                    command=task.command,
                    active=task.active,
                    create_time=task.create_time,
                    crontab_exp=task.crontab_exp,
                    command_input=task.command_input,
                )
                self.task_dict[task.id] = t_task
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
        from utils.thread_pool import main_loop

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

        self.task_finish_event.invoke(task_sess, loop=main_loop)
        if not task_sess.success:
            self.task_error_event.invoke(task_sess, loop=main_loop)

        out_file = output_store_path / f"{task_sess.id}.out"
        out_file.touch()

        with out_file.open("w+", encoding="utf-8") as file:
            # file.write(task_sess.info)
            # file.write(f"{task_sess.id} \n")
            file.write(task_sess.stdout)
        logger.debug("save the out put to %s", out_file.as_posix())
        logger.debug("%s session unmount and save=> %s", task_sess.id, task_sess)

    def mount_session(self, session: TaskExecutor):
        logger.debug("%s session mount => %s", session.id, session.raw_command)
        self.session_dict[session.id] = session

        with dataManager.session as sess:
            task = sess.query(TaskInfo).filter(TaskInfo.id == session.task_id).one()
            data_sess = SessionInfo(
                id=session.id,
                start_time=session.start_time,
                finish_time=session.finish_time,
                command=session.raw_command,
                command_input=session.command_input,
                task_id=session.task_id,
                task=task,
            )

            sess.add(data_sess)
            sess.commit()
        from utils.thread_pool import main_loop

        self.task_start_event.invoke(session, loop=main_loop)

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
            task_model = TaskInfo(
                id=new_task.id,
                name=new_task.name,
                active=new_task.active,
                create_time=new_task.create_time,
                command=new_task.command,
                crontab_exp=new_task.crontab_exp,
            )
            sess.add(task_model)
            sess.commit()

        if add_task.invoke_once:
            new_task.run()

        return new_task

    def modify_task(self, task_id: str, modify_task: TaskModifyForm) -> TaskUnit:
        """modify task

        Args:
            task_id (str): task id

            modify_task (TaskModifyForm): modify task form

        Returns:
            TaskUnit: modified task
        """
        task = self.task_dict[task_id]
        task.name = modify_task.name
        task.command = modify_task.command
        task.crontab_exp = modify_task.crontab_exp
        task.active = modify_task.active

        with dataManager.session as sess:
            task_model = sess.query(TaskInfo).filter(TaskInfo.id == task_id).one()
            task_model.name = task.name
            task_model.command = task.command
            task_model.crontab_exp = task.crontab_exp
            task_model.active = task.active
            sess.commit()

        return task


task_manager = TaskManager()
