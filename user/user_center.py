from utils.config import config
from utils.email_sender import EmailSender
from task_core.task_executor import TaskExecutor
from utils import logger
import psutil
import time


class SystemInfo:
    def __init__(self) -> None:
        self.cpu_usage_percent = 0.0
        self.memory_usage_percent = 0.0
        self.memory_usage = 0
        self.memory_total = 0

        self.network_sent_speed = 0
        self.network_recv_speed = 0

        self.network_sent_prev = 0
        self.network_recv_prev = 0

        self.last_refresh_time = 0
        self.refresh()

    def get_info(self) -> dict:
        if time.time() - self.last_refresh_time > 1:
            self.refresh()
        return {
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_percent": self.memory_usage_percent,
            "memory_usage": self.memory_usage,
            "memory_total": self.memory_total,
            "network_send_speed": self.network_sent_speed,
            "network_recv_speed": self.network_recv_speed,
        }

    def refresh(self):
        self.cpu_usage_percent = psutil.cpu_percent()
        self.memory_usage_percent = psutil.virtual_memory().percent
        self.memory_usage = psutil.virtual_memory().used
        self.memory_total = psutil.virtual_memory().total

        network_sent = psutil.net_io_counters().bytes_sent
        network_recv = psutil.net_io_counters().bytes_recv

        if self.network_sent_prev != 0:
            self.network_sent_speed = network_sent - self.network_sent_prev
        if self.network_recv_prev != 0:
            self.network_recv_speed = network_recv - self.network_recv_prev

        self.network_sent_prev = network_sent
        self.network_recv_prev = network_recv

        self.last_refresh_time = time.time()


class UserCenter:
    def __init__(self) -> None:
        self.inited = False
        self.email_sender = None

        self.system_info = SystemInfo()

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

        from task_core import task_manager, external_visit_manager

        task_unit = task_manager.get_task(task_exec.task_id)

        external = external_visit_manager.add_external_visit(task_exec.id)

        email_content: list[str] = []
        email_subject: list[str] = []

        if task_unit is None:
            email_content.append(
                f"task exector [{task_exec.id}=>{task_exec.command}] error: {task_exec.stderr}\nfrom TaskStack Auto Email",
            )
            email_subject.append(f"[TaskStack] {task_exec.command} run failed")
        else:
            email_content.append(
                f"[{task_unit.name}=>{task_unit.command}] run failed: {task_exec.stderr}\nfrom TaskStack Auto Email",
            )
            email_subject.append(f"[TaskStack] {task_unit.name} run failed")

        email_content.append(
            f"Quick visit link: {external.link}, valid time up to {external.expire_time}"
        )

        self.email_sender.send(
            config.email_config.receiver_email,
            "\n".join(email_content),
            "\n".join(email_subject),
        )

        logger.info("send email to %s", config.email_config.receiver_email)


user_center = UserCenter()
