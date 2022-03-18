import asyncio
from time import time
from math import sin
import websockets

url = "ws://127.0.0.1:3000/api/live/push/test_stream_id"
auth_token = "eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ=="
headers = [
    ("Authorization", f"Bearer {auth_token}")
]


async def main():
    async with websockets.connect(url, extra_headers=headers) as ws:
        while True:
            message = f"demo2,device=sensorA " \
                      f"value1={sin(time() * 5) * 100}," \
                      f"value2={sin(time() * 10) * 50}," \
                      f"value3={sin(time() * 2) * 70}\n"
            await ws.send(message)
            await asyncio.sleep(1/60)

asyncio.run(main())
