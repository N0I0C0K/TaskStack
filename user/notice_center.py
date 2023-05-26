import smtplib
from email.mime.text import MIMEText
from utils.config import config
from task_core.task_executor import TaskExecutor
from utils import logger


class EmailSender:
    __from_addr: str = None
    __pwd: str = None
    __emailer: smtplib.SMTP_SSL = None

    def __init__(self, from_addr, pwd, host: str) -> None:
        self.__from_addr = from_addr
        self.__pwd = pwd
        self.__host = host
        self.__emailer = smtplib.SMTP_SSL(self.__host, 465, timeout=10)
        self.__emailer.login(self.__from_addr, self.__pwd)

    def send(self, to_addr: str, content: str, subject: str) -> bool:
        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = self.__from_addr
        msg["To"] = to_addr
        self.__emailer = smtplib.SMTP_SSL(self.__host, 465, timeout=10)
        # self.__emailer.login(self.__from_addr, self.__pwd)
        try:
            self.__emailer.login(self.__from_addr, self.__pwd)
            self.__emailer.send_message(
                msg=msg, from_addr=self.__from_addr, to_addrs=to_addr
            )
            return True
        except smtplib.SMTPException as e:
            raise e


class NoticeCenter:
    def __init__(self) -> None:
        self.inited = False
        self.email_sender = None

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


notice_center = NoticeCenter()
