import asyncio
import shlex
import subprocess
import time
from typing import Callable

from utils import auto_decode, logger, uuid
from utils.thread_pool import main_loop


class TaskExecutor:
    def __init__(
        self, command: str, finish_callback: Callable = None, task_id: str = ""
    ) -> None:
        """
        任务执行单元
        :param session_info:`Session`类, 提供session的信息
        """
        assert len(command) > 0
        self.raw_command = command
        self.command = shlex.split(command)

        self.start_time = time.time()
        self.finish_time = 0

        self.id = uuid()
        self.task_id = task_id

        self.task = None
        self.__stdout = None
        self.__stderr = None

        self.finish_callback = finish_callback
        try:
            self.task = subprocess.Popen(
                self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except OSError as oserr:
            logger.error(oserr)
        except ValueError as valerr:
            logger.error(valerr)
        else:
            self.finish_check_task = main_loop.create_task(self.__finish_check())
        logger.info("Start execute => %s", self.command)

    async def __finish_check(self):
        while not self.finished:
            await asyncio.sleep(1)
        self.finish_time = time.time()

        if self.finish_callback:
            self.finish_callback()

    @property
    def finished(self) -> bool:
        return self.task is None or self.task.poll() is not None

    def kill(self):
        if self.task:
            self.task.kill()

    def wait(self, timeout=None):
        if not self.task:
            return
        self.task.wait(timeout)

    @property
    def stdout(self) -> str:
        if self.__stdout:
            return self.__stdout
        if self.task is None:
            return ""
        if not self.finished:
            logger.debug("attempt to access not finished process")
            return ""
        self.__stdout = auto_decode(self.task.stdout.read())
        return self.__stdout

    @property
    def stderr(self) -> str:
        if self.__stderr:
            return self.__stderr
        if self.task is None:
            return ""
        if not self.finished:
            logger.debug("attempt to access not finished process")
            return ""
        self.__stderr = auto_decode(self.task.stderr.read())
        return self.__stderr

    def __repr__(self) -> str:
        return f"{self.command}"
