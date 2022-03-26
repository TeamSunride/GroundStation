import logging

from gs_server.serial_input import SerialLineInput, FakeSerialLineInput
from gs_server.grafana_websocket import GrafanaLiveOutput
from gs_server.influxdb_output import InfluxDBOutput
import asyncio

logging.basicConfig(level=logging.INFO)

TIMESTAMP_PRECISION = "ms"

# serial_input = SerialLineInput("COM10", 2000000)
serial_input = FakeSerialLineInput()

grafana_output = GrafanaLiveOutput(
    host="localhost",
    port=3000,
    stream_id="test_stream_id",
    api_token="eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ==",
    timestamp_precision=TIMESTAMP_PRECISION
)
serial_input.add_output(grafana_output.output)

influxdb_output = InfluxDBOutput(
    host="localhost",
    port=8086,
    org_name="Sunride",
    bucket="telemetry",
    api_token="Cs0uiazCNzgsD-NAShVaDwBHk5RgGwx1LSu4OC5B1dQZyWnu0AhRPExoAvIJTBN0Jqde6B9R8YDnbZMjdEjmOg==",
    timestamp_precision=TIMESTAMP_PRECISION
)
serial_input.add_output(influxdb_output.output)

loop = asyncio.get_event_loop()
loop.create_task(grafana_output.connect())
loop.create_task(serial_input.connect())
loop.run_forever()
