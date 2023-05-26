from utils.config import config
from utils.email_sender import EmailSender
from task_core.task_executor import TaskExecutor
from utils import logger
import psutil
import time


class UserCenter:
    def __init__(self) -> None:
        self.inited = False
        self.email_sender = None
        self.last_system_info_fetch_time = None
        self.last_system_info = None

        from task_core.task_manager import task_manager

        task_manager.task_error_event += self.on_task_error_send_email

    def init_email_sender(self):
        if (
            config.email_config is not None
            and config.email_config.sender_email is not None
        ):
            try:
                self.email_sender = EmailSender(
                    config.email_config.sender_email,
                    config.email_config.sender_email_password,
                    config.email_config.sender_email_host,
                )
            except Exception as e:
                logger.error("email sender init error: %s", e)

    def init(self):
        self.init_email_sender()
        self.inited = True

    def on_task_error_send_email(self, task_exec: TaskExecutor):
        if self.email_sender is None:
            return

        from task_core.task_manager import task_manager

        task_unit = task_manager.get_task(task_exec.task_id)
        if task_unit is None:
            self.email_sender.send(
                config.email_config.receiver_email,
                f"task exector [{task_exec.id}=>{task_exec.command}] error: {task_exec.stderr}",
                f"task {task_exec.command} error",
            )
        else:
            self.email_sender.send(
                config.email_config.receiver_email,
                f"task [{task_unit.name}=>{task_unit.command}] error: {task_exec.stderr}",
                f"task {task_unit.name} error",
            )

    def get_system_info(self) -> dict:
        if (
            self.last_system_info_fetch_time is not None
            and time.time() - self.last_system_info_fetch_time < 1
        ):
            return self.last_system_info

        cpu_usage_percent = psutil.cpu_percent()
        memory_usage_percent = psutil.virtual_memory().percent
        memory_usage = psutil.virtual_memory().used
        memory_total = psutil.virtual_memory().total

        self.last_system_info_fetch_time = time.time()
        self.last_system_info = {
            "cpu_usage_percent": cpu_usage_percent,
            "memory_usage_percent": memory_usage_percent,
            "memory_usage": memory_usage,
            "memory_total": memory_total,
        }

        return self.last_system_info


user_center = UserCenter()
