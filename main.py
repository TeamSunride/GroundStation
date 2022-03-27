import logging

from gs_server.serial_input import SerialLineInput, FakeSerialLineInput
from gs_server.grafana_websocket import GrafanaLiveOutput
from gs_server.influxdb_output import InfluxDBOutput
from gs_server.config import conf
import asyncio

logging.basicConfig(level=logging.INFO)

# serial_input = SerialLineInput("COM10", 2000000)
serial_input = FakeSerialLineInput()

grafana_output = GrafanaLiveOutput(
    host=conf("GrafanaLiveOutput", "host"),
    port=conf("GrafanaLiveOutput", "port"),
    stream_id=conf("GrafanaLiveOutput", "stream_id"),
    api_token=conf("GrafanaLiveOutput", "api_token"),
    timestamp_precision=conf("timestamp_precision")
)
serial_input.add_output(grafana_output.output)

influxdb_output = InfluxDBOutput(
    host=conf("InfluxDBOutput", "host"),
    port=conf("InfluxDBOutput", "port"),
    org_name=conf("InfluxDBOutput", "org_name"),
    bucket=conf("InfluxDBOutput", "bucket"),
    api_token=conf("InfluxDBOutput", "api_token"),
    timestamp_precision=conf("timestamp_precision")
)
serial_input.add_output(influxdb_output.output)

loop = asyncio.get_event_loop()
loop.create_task(grafana_output.connect())
loop.create_task(serial_input.connect())
loop.run_forever()
