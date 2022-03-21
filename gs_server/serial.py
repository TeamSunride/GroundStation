import asyncio
from random import randint

import serial_asyncio
from serial.serialutil import SerialException
from logging import info, debug
from typing import Coroutine, List, Callable, Any
from time import time
from math import sin

# https://github.com/pyserial/pyserial-asyncio/blob/master/documentation/api.rst


class SerialLineInput:
    """
    Object that connects to a serial port, and calls a list of outputs when a line is read
    """

    # see the Streams documentation for information about these APIs
    # https://docs.python.org/3/library/asyncio-stream.html
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    port: str
    baudrate: int

    output_type = Callable[[str], Any]

    connected: bool = False

    outputs: List[output_type] = []

    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate

    async def connect(self):
        while not self.connected:
            info(f"Attempting to open Serial connection on port {self.port}")
            try:
                # open a serial connection to our Arduino
                self.reader, self.writer = await serial_asyncio.open_serial_connection(
                    url=self.port, baudrate=self.baudrate
                )
            except (ConnectionRefusedError, SerialException) as e:
                info(e)
                info(f"Connection refused on port {self.port}, retrying in 5 seconds...")
                await asyncio.sleep(5)
            else:
                info(f"Successfully opened Serial connection on port {self.port}")
                self.connected = True

        asyncio.create_task(self.listen())

    def add_output(self, output: output_type):
        self.outputs.append(output)

    async def listen(self):
        while self.connected:
            try:
                # read a line of data from the serial port
                line = await self.reader.readline()
            except (ConnectionResetError, SerialException):
                info(f"Connection lost on port {self.port}")
                self.connected = False

                # try to reconnect if connection was lost
                asyncio.create_task(self.connect())
            else:
                line = line.decode()
                # the gather function allows us to call all of our outputs concurrently
                # documentation is here https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently

                # we construct a list of coroutines with one argument, the line that was read
                output_coroutines = [output(line) for output in self.outputs]

                await asyncio.gather(*output_coroutines)


class FakeSerialLineInput:
    output_type = Callable[[str], Any]
    outputs: List[output_type] = []

    def add_output(self, output: output_type):
        self.outputs.append(output)

    async def connect(self):
        asyncio.create_task(self.listen())

    async def listen(self):
        while True:
            line = f"demo4,device=arduino_uno " \
                   f"value1={sin(time() * 10) + randint(-100, 100)/200}," \
                   f"value2={sin(time() * 5) * 2 + randint(-100, 100)/200} " \
                   f"{round(time() * 1000)}\n"

            output_coroutines = [output(line) for output in self.outputs]

            await asyncio.gather(*output_coroutines)

            await asyncio.sleep(1/25)
