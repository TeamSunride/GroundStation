import asyncio
import logging

import websockets
from typing import List, Tuple


class GrafanaLiveOutput:
    url: str
    auth_token: str
    headers: List[Tuple[str, str]]

    ws: websockets.WebSocketClientProtocol

    connected: bool = False
    remove_timestamp: bool

    logger: logging.Logger

    def __init__(self, url: str, auth_token: str, remove_timestamp: bool = True):
        self.url = url
        self.headers = [
            ("Authorization", f"Bearer {auth_token}")
        ]
        self.remove_timestamp = remove_timestamp

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
        if self.connected:
            await self.ws.send(output_string)
