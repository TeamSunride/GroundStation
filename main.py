import logging

from gs_server.serial import SerialLineInput, FakeSerialLineInput
from gs_server.grafana_websocket import GrafanaLiveOutput
import asyncio

logging.basicConfig(level=logging.INFO)


async def my_output(output_str: str):
    # print(output_str)
    pass


# serial_input = SerialLineInput("COM4", 9600)
serial_input = FakeSerialLineInput()
serial_input.add_output(my_output)

grafana_output = GrafanaLiveOutput(
    url="ws://127.0.0.1:3000/api/live/push/test_stream_id",
    auth_token="eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ=="
)
serial_input.add_output(grafana_output.output)

loop = asyncio.get_event_loop()
loop.create_task(grafana_output.connect())
loop.create_task(serial_input.connect())
loop.run_forever()
