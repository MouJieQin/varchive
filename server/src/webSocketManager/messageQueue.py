#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

from queue import Queue

class MessageQueue:
    def __init__(self, maxsize: int):
        self.q = Queue(maxsize)

    def full(self) -> bool:
        return self.q.full()

    def empty(self) -> bool:
        return self.q.empty()

    def clear(self):
        while not self.empty():
            self.get()

    def put(self, message: str):
        if self.full():
            self.q.get()
        self.q.put(message)

    def qsize(self) -> int:
        return self.q.qsize()

    def get(self) -> str:
        return self.q.get()
