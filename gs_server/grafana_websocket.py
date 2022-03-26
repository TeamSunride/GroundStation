import asyncio
import logging

import websockets
from typing import List, Tuple


class GrafanaLiveOutput:
    url: str
    headers: List[Tuple[str, str]]

    ws: websockets.WebSocketClientProtocol

    connected: bool = False
    timestamp_precision: str  # "us", "ms", or "s"

    logger: logging.Logger

    def __init__(self, host: str, port: int, stream_id: str, api_token: str, timestamp_precision: str = "ms",
                 ssl: bool = False):
        self.url = f"ws{'s' if ssl else ''}://{host}:{port}/api/live/push/{stream_id}"
        self.headers = [
            ("Authorization", f"Bearer {api_token}")
        ]
        self.timestamp_precision = timestamp_precision

        self.logger = logging.getLogger(self.__class__.__name__)

    async def connect(self):
        while not self.connected:
            try:
                self.logger.info(f"Connecting to url {self.url}")
                self.ws = await websockets.connect(self.url, extra_headers=self.headers)
            except websockets.InvalidURI as e:
                self.logger.info(e)
                break
            except (websockets.InvalidHandshake, TimeoutError, ConnectionRefusedError) as e:
                self.logger.info(e)
                self.logger.info(f"Attempting to reconnect to url {self.url} in 5 seconds")
                await asyncio.sleep(5)
            else:
                self.logger.info(f"Grafana WebSocket Connection Successful")
                self.connected = True

        asyncio.create_task(self.listen())

    async def listen(self):
        while self.connected:
            try:
                await self.ws.recv()  # raises ConnectionClosed if the connection is lost
            except websockets.ConnectionClosed:
                self.logger.info(f"Lost connection to url {self.url}")
                self.connected = False
                asyncio.create_task(self.connect())

    async def output(self, output_string: str):
        if not self.connected:
            return

        # grafana live appears to want a timestamp precision in nanoseconds else time series graphs don't work

        # so we first determine if the input string contains a timestamp
        possible_timestamp_position = output_string.rfind(" ") + 1
        possible_timestamp = output_string[possible_timestamp_position:].strip("\n")
        has_timestamp = possible_timestamp.isdigit()

        # if no timestamp is given then send the string straight to grafana and hope for the best
        if not has_timestamp:
            return await self.ws.send(output_string)

        # if the input timestamp is already in nanoseconds, do not bother doing more slow processing
        if self.timestamp_precision == "ns":
            return await self.ws.send(output_string)

        # cover all other cases of timestamp precision
        if self.timestamp_precision in ["ms", "us", "s"]:

            # a switch statement would be used here but was only just implemented in python 3.10
            multiplier = \
                1_000_000_000 if self.timestamp_precision == "s" else \
                1_000_000 if self.timestamp_precision == "ms" else \
                1_000 if self.timestamp_precision == "us" else ''

            timestamp = int(possible_timestamp)
            new_timestamp = timestamp * multiplier  # convert to nanoseconds
            output_string = output_string[:possible_timestamp_position] + str(new_timestamp)
            return await self.ws.send(output_string)

        # if the timestamp precision is something else then hope for the best and send it anyway
        return await self.ws.send(output_string)
