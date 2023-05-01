import asyncio
import shlex

# import subprocess
import time
from asyncio import subprocess
from asyncio.subprocess import Process
from typing import Callable

from chardet import UniversalDetector

from utils import auto_decode, logger, uuid
from utils.thread_pool import thread_pool


class TaskExecutor:
    def __init__(
        self, command: str, finish_callback: Callable | None = None, task_id: str = ""
    ) -> None:
        """
        任务执行单元
        :param session_info:`Session`类, 提供session的信息
        """
        assert len(command) > 0
        self.raw_command = command
        self.command = shlex.split(command)

        self.start_time = time.time()
        self.finish_time = 0.0

        self.id = uuid()
        self.task_id = task_id

        self.task: Process | None = None
        self.__stdout = ""
        self.__stderr = ""

        self.finish_callback = finish_callback
        self.finish_check_task: asyncio.Task | None = None

        self.decode_detector = UniversalDetector()

        self.stdout_lock = asyncio.Lock()

        self.__running = False

        from utils.thread_pool import main_loop

        self.__run_process_task = main_loop.create_task(self.run_process())

    async def wait_until_run(self):
        await self.__run_process_task

    async def run_process(self):
        try:
            self.task = await asyncio.create_subprocess_shell(
                self.raw_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.__running = True
        except OSError as oserr:
            logger.error(oserr)
            raise oserr
        except ValueError as valerr:
            logger.error(valerr)
            raise valerr
        else:
            from utils.thread_pool import main_loop

            self.finish_check_task = main_loop.create_task(self.__finish_check())
            logger.info("Start execute => %s", self.command)

    async def __finish_check(self):
        await self.task.wait()
        logger.info("%s[task:%s] run finished", self.raw_command, self.task_id)
        self.__running = False
        self.finish_time = time.time()

        await self.flush_stdout()

        if self.finish_callback:
            self.finish_callback()

    @property
    def success(self) -> bool:
        return self.finished and self.task.returncode == 0

    @property
    def finished(self) -> bool:
        return self.task is not None and not self.__running

    @property
    def running(self) -> bool:
        return self.__running

    async def kill(self):
        if self.task:
            self.task.kill()
            await self.wait()

    def __decode(self, src: bytes) -> str:
        if not self.decode_detector.done:
            self.decode_detector.feed(src)
        if not self.decode_detector.done:
            return src.decode()
        return src.decode(self.decode_detector.result["encoding"])

    async def wait(self, timeout: float | None = None) -> int:
        if self.finish_check_task is None:
            raise ValueError
        await self.finish_check_task
        return self.task.returncode

    async def readline(self) -> str:
        if not self.running or self.task.stdout is None:
            return ""
        async with self.stdout_lock:
            line_byte = await self.task.stdout.readline()
        if len(line_byte) == 0:
            # in order to prevent too fast response block the thread
            await asyncio.sleep(0.1)
            return ""
        line_str = self.__decode(line_byte)
        self.__stdout += line_str
        return line_str

    async def flush_stdout(self) -> str:
        async with self.stdout_lock:
            self.__stdout += self.__decode(await self.task.stdout.read())
            self.__stderr += self.__decode(await self.task.stderr.read())
        return self.__stdout

    @property
    def stdout(self) -> str:
        return self.__stdout

    @property
    def stderr(self) -> str:
        return self.__stderr

    def __repr__(self) -> str:
        return f"{self.command}"
