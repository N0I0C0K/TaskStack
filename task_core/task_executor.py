import asyncio
import shlex

# import subprocess
import time
from asyncio import subprocess
from asyncio.subprocess import Process
from typing import Callable

from chardet import UniversalDetector

from utils import auto_decode, logger, uuid, formate_time


class TaskExecutor:
    def __init__(
        self,
        command: str,
        finish_callback: Callable | None = None,
        task_id: str = "",
        loop: asyncio.AbstractEventLoop | None = None,
        command_input: str | None = None,
    ) -> None:
        """TaskExector init

        Args:
            command (str): which will be executed

            finish_callback (Callable | None, optional): if this command run finished then will call this func. Defaults to None.

            task_id (str, optional): from which task unit. Defaults to "".

            loop (asyncio.AbstractEventLoop | None, optional): which loop this command run in. Defaults to None.

            input (str | None, optional): command's input. Defaults to None(no input).
        """
        assert len(command) > 0
        self.raw_command = command
        self.command = command
        self.command_input = command_input

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

        self.__task_run_loop = asyncio.get_running_loop() if loop is None else loop

        self.__run_process_task = self.__task_run_loop.create_task(self.run_process())
        self.__started = asyncio.Event()

    async def wait_until_run(self):
        """wait until this task start running"""
        await self.__run_process_task

    async def run_process(self):
        try:
            self.task = await asyncio.create_subprocess_shell(
                self.raw_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
            self.__running = True
            if self.command_input is not None:
                self.task.stdin.write(self.command_input.encode())
        except OSError as oserr:
            logger.error(oserr)
            raise oserr
        except ValueError as valerr:
            logger.error(valerr)
            raise valerr
        else:
            self.finish_check_task = self.__task_run_loop.create_task(
                self.__finish_check()
            )
            logger.info("Start execute => %s", self.raw_command)
            self.__started.set()

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
            return src.decode(errors="replace")
        return src.decode(self.decode_detector.result["encoding"])

    async def __decode_async(self, src: bytes) -> str:
        return await self.__task_run_loop.run_in_executor(None, self.__decode, src)

    async def wait(self, timeout: float | None = None) -> int:
        await self.wait_until_run()
        if self.finish_check_task is not None:
            await self.finish_check_task
        else:
            logger.warning("task finish callback is None")
            raise ValueError
        return self.task.returncode

    async def readline(self) -> str:
        """read a line from stdout.

        Returns:
            str: a line from stdout
        """
        if not self.running or self.task.stdout is None:
            return ""
        async with self.stdout_lock:
            line_byte = await self.task.stdout.readline()
        if len(line_byte) == 0:
            # in order to prevent too fast response block the thread
            await asyncio.sleep(0.1)
            return ""
        line_str = await self.__decode_async(line_byte)
        self.__stdout += line_str
        return line_str

    async def flush_stdout(self) -> str:
        """
        flush stdout and stderr completely.(if not finished, will block the thread)
        """
        async with self.stdout_lock:
            self.__stdout += await self.__decode_async(await self.task.stdout.read())
            self.__stderr += await self.__decode_async(await self.task.stderr.read())
        return self.__stdout

    @property
    def stdout(self) -> str:
        return self.__stdout

    @property
    def stderr(self) -> str:
        return self.__stderr

    @property
    def returncode(self) -> int | None:
        return self.task.returncode if self.task else None

    @property
    def info(self) -> str:
        return (
            f"Session id: {self.id}\n"
            f"{formate_time(self.start_time)}-{formate_time(self.finish_time)}\n"
            f"From task: {self.task_id}\n"
            f"Command: {self.raw_command}\n"
            f"Input: {'' if self.command_input is None else self.command_input}\n"
        )

    def __repr__(self) -> str:
        return self.info
