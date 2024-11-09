#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import os
import subprocess
import threading
import asyncio
import time
import inspect
from typing import *


class SystemRun:
    def __init__(self):
        self.taskQueue: List[Dict] = []

        def run_async_task():
            asyncio.run(self.__run())

        systemRunThread = threading.Thread(target=run_async_task)
        systemRunThread.daemon = True
        systemRunThread.start()

    def put(self, command: List[str], callback: Callable = None, *args, **kwargs):
        self.taskQueue.append(
            {"command": command, "callback": callback, "args": args, "kwargs": kwargs}
        )

    def size(self) -> int:
        return len(self.taskQueue)

    def empty(self) -> bool:
        return self.size() == 0

    async def __run(self):
        while True:
            while not self.empty():
                task = self.taskQueue.pop(0)
                res = subprocess.run(
                    args=task["command"], capture_output=True, text=True
                )
                if task["callback"]:
                    if inspect.iscoroutinefunction(task["callback"]):
                        await task["callback"](res, *task["args"], **task["kwargs"])
                    else:
                        task["callback"](res, *task["args"], **task["kwargs"])
            await asyncio.sleep(0.05)
