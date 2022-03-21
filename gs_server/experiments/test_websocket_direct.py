import websocket
from time import sleep, time, time_ns
from math import sin

ws = websocket.WebSocket()
ws.connect(
    "ws://127.0.0.1:3000/api/live/push/test_stream_id", 
    header=["Authorization: Bearer eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ=="]
)

while True:
    message = f"demo2,device=sensorA " \
              f"value1={sin(time()) * 100}," \
              f"value2={sin(time()) * 50}," \
              f"value3={sin(time() * 2) * 70}\n"
    print(message)
    ws.send(message)
    sleep(1/50)


# TODO: this connection breaks after a few seconds, so fix that (refer to docs for websocket!)
