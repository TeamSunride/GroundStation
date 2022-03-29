import logging
from gs_server import *
import asyncio

# configure the logging module to output the "INFO" log level
logging.basicConfig(level=logging.INFO)

# create a variable that defines the input timestamp precision
TIMESTAMP_PRECISION = "ms"

# serial_input = SerialLineInput("COM10", 2000000)
serial_input = FakeSerialLineInput()

# define our GrafanaLiveOutput object
grafana_output = GrafanaLiveOutput(
    host="localhost",
    port=3000,
    stream_id="test_stream_id",
    api_token="eyJrIjoic2xET3E3aTRZOGE2RjNGdk54MUc5ZGU0TEE0SWpnZk4iLCJuIjoidGVzdCIsImlkIjoxfQ==",
    timestamp_precision=TIMESTAMP_PRECISION
)
# plug in our GrafanaLiveOutput to our SerialLineInput
serial_input.add_output(grafana_output.input)

# define our InfluxDBOutput object
influxdb_output = InfluxDBOutput(
    host="localhost",
    port=8086,
    org_name="Sunride",
    bucket="telemetry",
    api_token="Cs0uiazCNzgsD-NAShVaDwBHk5RgGwx1LSu4OC5B1dQZyWnu0AhRPExoAvIJTBN0Jqde6B9R8YDnbZMjdEjmOg==",
    timestamp_precision=TIMESTAMP_PRECISION
)
# plug in our InfluxDBOutput to our SerialLineInput
serial_input.add_output(influxdb_output.input)

# get asyncio event loop and connect the serial/grafana inputs/outputs
loop = asyncio.get_event_loop()
loop.create_task(grafana_output.connect())
loop.create_task(serial_input.connect())
try:
    # run the loop forever
    loop.run_forever()
except KeyboardInterrupt:  # prevent an error from showing when the script is closed
    print("Stopping...")
