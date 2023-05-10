import time
from dataclasses import dataclass, field

from utils import logger, uuid
from utils.scheduler import CronTrigger, Job, scheduler

from .task_executor import TaskExecutor


# from functools import wraps


class AlreadyOnTheRun(Exception):
    pass


class CantRunTask(Exception):
    pass


class NotRunning(Exception):
    pass


@dataclass
class TaskUnit:
    name: str
    command: str
    active: bool = True
    crontab_exp: str | None = None
    command_input: str | None = None
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

        if self.task_exectuor is None:
            return
        logger.info("%s-%s finish execute", self.name, self.id)
        task_manager.unmount_save_session(self.task_exectuor.id)

    def run(self) -> str:
        if not self.can_exec():
            raise CantRunTask()
        from .task_manager import task_manager
        from utils.thread_pool import main_loop

        self.task_exectuor = TaskExecutor(
            self.command,
            self.__on_task_finish,
            task_id=self.id,
            loop=main_loop,
            input=self.command_input,
        )

        self.last_exec_time = time.time()
        task_manager.mount_session(self.task_exectuor)
        return self.task_exectuor.id

    async def stop(self) -> bool:
        if not self.running:
            raise NotRunning
        await self.task_exectuor.kill()
        return True

    def __task_exec_func(self):
        logger.info("%s-%s scheduler start execute", self.name, self.id)
        if not self.can_exec():
            return
        self.run()
        logger.info("%s-%s scheduler execute success", self.name, self.id)

    def __post_init__(self):
        if self.crontab_exp is not None and len(self.crontab_exp) > 0:
            self.scheduler_job = scheduler.add_job(
                self.__task_exec_func,
                CronTrigger.from_crontab(self.crontab_exp),
            )
            if not self.active:
                self.scheduler_job.pause()

    def set_active(self, val: bool):
        if val == self.active:
            raise AlreadyOnTheRun()
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
        return self.task_exectuor is not None and self.task_exectuor.running

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "active": self.active,
            "create_time": self.create_time,
            "last_exec_time": self.last_exec_time,
            "command": self.command,
            "crontab_exp": self.crontab_exp,
            "running": self.running,
        }
