import asyncio
import logging
from random import randint

import serial_asyncio
from serial.serialutil import SerialException
from typing import Coroutine, List, Callable, Any
from time import time, time_ns
from math import sin

import re
import ast
from influx_line_protocol import Metric, MetricCollection

# https://github.com/pyserial/pyserial-asyncio/blob/master/documentation/api.rst


class LineProtocolInput:
    """
    Base class which should be inherited from. Contains the tooling for calling outputs
    """

    output_type = Callable[[str], Any]
    outputs: List[output_type] = []

    def add_output(self, output: output_type):
        self.outputs.append(output)

    async def call_outputs(self, line):
        output_coroutines = [
            asyncio.create_task(output(line)) for output in self.outputs
        ]

        await asyncio.gather(*output_coroutines)


class SerialLineInput(LineProtocolInput):
    """
    Object that connects to a serial port, and calls a list of outputs when a line is read
    """

    # see the Streams documentation for information about these APIs
    # https://docs.python.org/3/library/asyncio-stream.html
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

    port: str
    baudrate: int
    connected: bool = False
    logger: logging.Logger

    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate
        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self):
        while not self.connected:
            self.logger.info(
                f"Attempting to open Serial connection on port {self.port}"
            )
            try:
                # open a serial connection to our Arduino
                self.reader, self.writer = await serial_asyncio.open_serial_connection(
                    url=self.port, baudrate=self.baudrate
                )
            except (ConnectionRefusedError, SerialException) as e:
                self.logger.info(e)
                self.logger.info(
                    f"Connection refused on port {self.port}, retrying in 5 seconds..."
                )
                await asyncio.sleep(5)
            else:
                self.logger.info(
                    f"Successfully opened Serial connection on port {self.port}"
                )
                self.connected = True

        asyncio.create_task(self.listen())

    async def listen(self):
        while self.connected:
            try:
                # read a line of data from the serial port
                line = await self.reader.readline()
            except (ConnectionResetError, SerialException):
                self.logger.info(f"Connection lost on port {self.port}")
                self.connected = False

                # try to reconnect if connection was lost
                asyncio.create_task(self.connect())
            else:
                # line = line.decode().strip("\n").strip("\r") + "\n"
                # await self.call_outputs(line)

                line = line.decode()

                try:
                    line_id = re.search(r"(.*),", line)
                    metric = Metric(line_id.group(1))

                    line_time = re.search(r"\d+$", line)
                    metric.with_timestamp(int(line_time.group(0)))

                    line_splits = line.split(maxsplit=1)
                    tag_sets = re.findall(r"([^\s,]+)=([^\s,]+)", line_splits[0])
                    field_sets = re.findall(r"([^\s,]+)=([^\s,]+)", line_splits[1])
                    for tag_set in tag_sets:
                        metric.add_tag(tag_set[0], tag_set[1])
                    for field_set in field_sets:
                        # TODO: What type are the values?
                        try:
                            ast.literal_eval(field_set[1])
                        except ValueError:
                            metric.add_value(field_set[0], field_set[1])

                        metric.add_value(field_set[0], ast.literal_eval(field_set[1]))
                except:
                    pass
                else:
                    await self.call_outputs(metric)


class FakeSerialLineInput(LineProtocolInput):
    """
    Fake serial input used for development
    """

    output_type = Callable[[str], Any]
    outputs: List[output_type] = []

    def add_output(self, output: output_type):
        self.outputs.append(output)

    async def connect(self):
        asyncio.create_task(self.listen())

    async def listen(self):
        while True:
            line = (
                f"demo4,device=arduino_uno "
                f"value1={sin(time() * 10) + randint(-100, 100) / 200},"
                f"value2={sin(time() * 5) * 2 + randint(-100, 100) / 200} "
                f"{round(time() * 1000)}\n"
            )

            await self.call_outputs(line)
            await asyncio.sleep(1 / 30)
