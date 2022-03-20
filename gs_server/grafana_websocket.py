import asyncio

import websockets
from typing import List, Tuple
from logging import info


class GrafanaLiveOutput:
    url: str
    auth_token: str
    headers: List[Tuple[str, str]]

    ws: websockets.WebSocketClientProtocol

    connected: bool = False

    def __init__(self, url: str, auth_token: str):
        self.url = url
        self.headers = [
            ("Authorization", f"Bearer {auth_token}")
        ]

    async def connect(self):
        while not self.connected:
            try:
                info(f"Connecting to url {self.url}")
                self.ws = await websockets.connect(self.url, extra_headers=self.headers)
            except websockets.InvalidURI as e:
                info(e)
                break
            except (websockets.InvalidHandshake, TimeoutError, ConnectionRefusedError) as e:
                info(e)
                info(f"Attempting to reconnect to url {self.url} in 5 seconds")
                await asyncio.sleep(5)
            else:
                info(f"Connection successful")
                self.connected = True

        asyncio.create_task(self.listen())

    async def listen(self):
        while self.connected:
            try:
                await self.ws.recv()  # raises ConnectionClosed if the connection is lost
            except websockets.ConnectionClosed:
                info(f"Lost connection to url {self.url}")
                self.connected = False
                asyncio.create_task(self.connect())

    async def output(self, output_string: str):
        if self.connected:
            await self.ws.send(output_string)
