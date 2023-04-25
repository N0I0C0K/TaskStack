from dataclasses import dataclass, field
from utils.scheduler import scheduler, Job, CronTrigger
from .task_executor import TaskExecutor
from utils import logger, uuid

import time

# from functools import wraps


class AlreadyOnTheRun(Exception):
    pass


class CantRunTask(Exception):
    pass


@dataclass
class TaskUnit:
    name: str
    command: str
    active: bool = True
    crontab_exp: str = ""
    id: str = field(default_factory=uuid)
    create_time: float = field(default_factory=time.time)

    scheduler_job: Job | None = field(init=False, default=None)
    task_exectuor: TaskExecutor | None = field(init=False, default=None)
    last_exec_time: float = field(init=False, default=0.0)

    def can_exec(self) -> bool:
        return not (
            self.command is None
            or len(self.command) <= 1
            or (self.task_exectuor is not None and not self.task_exectuor.finished)
        )

    def __on_task_finish(self):
        from .task_manager import task_manager

        logger.info("%s-%s finish execute", self.name, self.id)
        task_manager.unmount_save_session(self.task_exectuor.id)

    def run(self) -> str:
        if not self.can_exec():
            raise CantRunTask()
        from .task_manager import task_manager

        self.task_exectuor = TaskExecutor(self.command, self.__on_task_finish)
        self.last_exec_time = time.time()
        task_manager.mount_session(self.task_exectuor)
        return self.task_exectuor.id

    def __task_exec_func(self):
        if self.can_exec():
            return
        logger.info("%s-%s start execute", self.name, self.id)
        self.run()

    def __post_init__(self):
        if self.crontab_exp is not None and len(self.crontab_exp) > 0:
            self.scheduler_job = scheduler.add_job(
                self.__task_exec_func,
                CronTrigger.from_crontab(self.crontab_exp),
            )

    def set_active(self, val: bool):
        if val == self.active:
            raise AlreadyOnTheRun("task is running")
        self.active = val
        if val:
            if self.scheduler_job is not None:
                self.scheduler_job.resume()
                logger.debug("%s-%s task resumed", self.id, self.name)
        else:
            if self.scheduler_job is not None:
                self.scheduler_job.pause()
                logger.debug("%s-%s task paused", self.id, self.name)

    @property
    def running(self) -> bool:
        return self.task_exectuor is not None and not self.task_exectuor.finished

    def to_dict(self) -> dict:
        # return {
        #     "id": self.id,
        #     "name": self.name,
        #     "active": self.active,
        #     "create_time": self.create_time,
        #     "command": self.command,
        #     "crontab_exp": self.crontab_exp,
        # }
        return self.__dict__ | {"running": self.running}
