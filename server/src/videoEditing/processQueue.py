#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import subprocess

# from concurrent.futures import ThreadPoolExecutor
import threading
from typing import *
from enum import Enum
import time
import inspect
import asyncio


class TaskInfo(str, Enum):
    KEY = "key"
    COMMAND = "command"
    STATUS = "status"
    PROCESS = "process"
    CALLBACK = "callback"
    ARGS = "args"
    KWARGS = "kwargs"


class TaskStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    FAILED = "failed"
    CANCELED = "canceled"
    DONE = "done"


class node:
    def __init__(self, pre, next, val: any):
        self.pre: node = pre
        self.next: node = next
        self.val: any = val
class Deque:
    def __init__(self):
        self.__head = node(None, None, None)
        self.__tail = node(None, None, None)
        self.__head.next = self.__tail
        self.__tail.pre = self.__head
        self.count = 0

    def begin(self) -> node:
        return self.__head.next

    def end(self) -> node:
        return self.__tail

    def last(self) -> node:
        return self.__tail.pre

    def empty(self) -> bool:
        return self.size() == 0

    def size(self) -> int:
        return self.count

    def insert(self, pos: node, val: any) -> node:
        preNode = pos.pre
        newNode = node(preNode, pos, val)
        preNode.next = newNode
        pos.pre = newNode
        self.count += 1
        return newNode

    def put(self, val: any) -> node:
        return self.insert(self.__tail, val)

    def remove(self, pos: node):
        preNode = pos.pre
        nextNode = pos.next
        preNode.next = nextNode
        nextNode.pre = preNode
        self.count -= 1

    def removeAndReturnNext(self, pos: node) -> node:
        nextNode = pos.next
        self.remove(pos)
        return nextNode

    def pop(self) -> node:
        lastNode = self.begin()
        self.remove(lastNode)
        return lastNode


class ProcessQueue:
    def __init__(self, maxSize: int):
        self.maxSize = maxSize
        self.runningCount = 0
        self.tasks: Deque = Deque()
        self.keyMapTask: Dict[str:node] = {}
        self.taskList = []
        self.keysCanceled = []

        def run_async_task():
            asyncio.run(self.__run())

        processManagerThread = threading.Thread(target=run_async_task)
        processManagerThread.daemon = True
        processManagerThread.start()

    def empty(self):
        return self.size() == 0

    def size(self):
        return self.tasks.count

    async def __run(self):
        while True:
            try:
                await self.__runImple()
            except Exception as e:
                print(
                    "This exception may be normal because files have been deleted.{}".format(
                        e
                    )
                )
                # self.cancelAll()
            time.sleep(0.01)

    async def __runImple(self):
        while len(self.taskList) != 0:
            taskInfo = self.taskList.pop(0)
            task = self.tasks.put(taskInfo)
            if inspect.iscoroutinefunction(task.val[TaskInfo.CALLBACK]):
                await task.val[TaskInfo.CALLBACK](
                    TaskStatus.READY,
                    *task.val[TaskInfo.ARGS],
                    **task.val[TaskInfo.KWARGS]
                )
            else:
                task.val[TaskInfo.CALLBACK](
                    TaskStatus.READY,
                    *task.val[TaskInfo.ARGS],
                    **task.val[TaskInfo.KWARGS]
                )
            self.keyMapTask[taskInfo[TaskInfo.KEY]] = task
        while len(self.keysCanceled) != 0:
            key = self.keysCanceled.pop(0)
            if key in self.keyMapTask.keys():
                task: node = self.keyMapTask[key]
                if task.val[TaskInfo.STATUS] == TaskStatus.RUNNING:
                    task.val[TaskInfo.PROCESS].terminate()
                if inspect.iscoroutinefunction(task.val[TaskInfo.CALLBACK]):
                    await task.val[TaskInfo.CALLBACK](
                        TaskStatus.CANCELED,
                        *task.val[TaskInfo.ARGS],
                        **task.val[TaskInfo.KWARGS]
                    )
                else:
                    task.val[TaskInfo.CALLBACK](
                        TaskStatus.CANCELED,
                        *task.val[TaskInfo.ARGS],
                        **task.val[TaskInfo.KWARGS]
                    )
                self.keyMapTask.pop(task.val[TaskInfo.KEY])
                self.tasks.remove(task)
        runningCount = 0
        task = self.tasks.begin()
        end = self.tasks.end()
        while task != end:
            if runningCount >= self.maxSize:
                break
            if task.val[TaskInfo.STATUS] == TaskStatus.RUNNING:
                process: subprocess.Popen = task.val[TaskInfo.PROCESS]
                if process.poll() == 0:
                    if inspect.iscoroutinefunction(task.val[TaskInfo.CALLBACK]):
                        await task.val[TaskInfo.CALLBACK](
                            TaskStatus.DONE,
                            *task.val[TaskInfo.ARGS],
                            **task.val[TaskInfo.KWARGS]
                        )
                    else:
                        task.val[TaskInfo.CALLBACK](
                            TaskStatus.DONE,
                            *task.val[TaskInfo.ARGS],
                            **task.val[TaskInfo.KWARGS]
                        )
                    self.keyMapTask.pop(task.val[TaskInfo.KEY])
                    task = self.tasks.removeAndReturnNext(task)
                    print("task size:", self.tasks.size())
                elif process.poll() == None:
                    runningCount += 1
                    task = task.next
                else:
                    if inspect.iscoroutinefunction(task.val[TaskInfo.CALLBACK]):
                        await task.val[TaskInfo.CALLBACK](
                            TaskStatus.FAILED,
                            *task.val[TaskInfo.ARGS],
                            **task.val[TaskInfo.KWARGS]
                        )
                    else:
                        task.val[TaskInfo.CALLBACK](
                            TaskStatus.FAILED,
                            *task.val[TaskInfo.ARGS],
                            **task.val[TaskInfo.KWARGS]
                        )
                    self.keyMapTask.pop(task.val[TaskInfo.KEY])
                    task = self.tasks.removeAndReturnNext(task)
            elif task.val[TaskInfo.STATUS] == TaskStatus.READY:
                task.val[TaskInfo.PROCESS] = subprocess.Popen(
                    task.val[TaskInfo.COMMAND], shell=True
                )
                if inspect.iscoroutinefunction(task.val[TaskInfo.CALLBACK]):
                    await task.val[TaskInfo.CALLBACK](
                        TaskStatus.RUNNING,
                        *task.val[TaskInfo.ARGS],
                        **task.val[TaskInfo.KWARGS]
                    )
                else:
                    task.val[TaskInfo.CALLBACK](
                        TaskStatus.RUNNING,
                        *task.val[TaskInfo.ARGS],
                        **task.val[TaskInfo.KWARGS]
                    )
                task.val[TaskInfo.STATUS] = TaskStatus.RUNNING
                runningCount += 1
                task = task.next
            else:
                # Never Happen
                print("Never Happen.")

    def put(self, key: str, command: str, callback: Callable, *args, **kwargs):
        if self.hasKey(key):
            return
        self.taskList.append(
            {
                TaskInfo.KEY: key,
                TaskInfo.COMMAND: command,
                TaskInfo.CALLBACK: callback,
                TaskInfo.STATUS: TaskStatus.READY,
                TaskInfo.PROCESS: "",
                TaskInfo.ARGS: args,
                TaskInfo.KWARGS: kwargs,
            }
        )
        # print(self.taskList)

    def hasKey(self, key: str) -> bool:
        return key in self.keyMapTask.keys()

    def cancel(self, key: str):
        if self.hasKey(key):
            self.keysCanceled.append(key)

    def cancelAll(self):
        for key in self.keyMapTask.keys():
            self.keysCanceled.append(key)
