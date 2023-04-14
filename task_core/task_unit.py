from dataclasses import dataclass, field
from utils.scheduler import scheduler, Job, CronTrigger
from .task_executor import TaskExecutor
from utils import logger


@dataclass
class TaskUnit:
    id: str
    name: str
    active: bool
    create_time: float
    command: str
    crontab_exp: str | None = None
    scheduler_job: Job = field(init=False, default=None)
    task_exectuor: TaskExecutor = field(init=False, default=None)

    def can_exec(self) -> bool:
        return not (
            self.command is None
            or len(self.command) <= 1
            or (self.task_exectuor is not None and not self.task_exectuor.finished())
        )

    def __on_task_finish(self):
        from .task_manager import task_manager

        logger.info("%s-%s finish execute", self.name, self.id)
        task_manager.unmount_save_session(self.task_exectuor.id)

    def run_task(self):
        if not self.can_exec():
            return
        from .task_manager import task_manager

        self.task_exectuor = TaskExecutor(self.command, self.__on_task_finish)
        task_manager.mount_session(self.task_exectuor)

    def __task_exec_func(self):
        if self.can_exec():
            return
        logger.info("%s-%s start execute", self.name, self.id)
        self.run_task()

    def __post_init__(self):
        if self.crontab_exp is not None:
            self.scheduler_job = scheduler.add_job(
                self.__task_exec_func, CronTrigger.from_crontab(self.crontab_exp)
            )
