#! /usr/bin/env python3.9
# _*_coding:utf-8_*_

import asyncio
import threading
from typing import *


class ThreadAsync:
    def __init__(self):
        # List to store the async functions to be executed
        self.async_functions = []
        # Start the asyncio event loop in a separate thread
        thread = threading.Thread(target=self.__start_async_loop)
        thread.daemon = True
        thread.start()

    # Start the asyncio event loop in a separate thread
    def __start_async_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(self.__run_async_functions())
        loop.run_forever()

    # This function runs the async functions
    async def __run_async_functions(self):
        while True:
            if self.async_functions:
                func = self.async_functions.pop(0)
                await func()
            else:
                await asyncio.sleep(0.1)

    # Function to add new async function to be executed
    def addAsyncFunction(self, func: Callable):
        self.async_functions.append(func)
