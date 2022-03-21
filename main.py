import logging

from gs_server.serial import SerialLineInput, FakeSerialLineInput
from gs_server.grafana_websocket import GrafanaLiveOutput
from gs_server.influxdb_output import InfluxDBOutput
import asyncio

logging.basicConfig(level=logging.INFO)


# serial_input = SerialLineInput("COM4", 9600)
serial_input = FakeSerialLineInput()

grafana_output = GrafanaLiveOutput(
    url="ws://127.0.0.1:3000/api/live/push/test_stream_id",
    auth_token="eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ=="
)
serial_input.add_output(grafana_output.output)

influxdb_output = InfluxDBOutput(
    host="localhost",
    port=8086,
    org_name="Sunride",
    bucket="telemetry",
    api_token="Cs0uiazCNzgsD-NAShVaDwBHk5RgGwx1LSu4OC5B1dQZyWnu0AhRPExoAvIJTBN0Jqde6B9R8YDnbZMjdEjmOg=="
)
serial_input.add_output(influxdb_output.output)

loop = asyncio.get_event_loop()
loop.create_task(grafana_output.connect())
loop.create_task(serial_input.connect())
loop.run_forever()
