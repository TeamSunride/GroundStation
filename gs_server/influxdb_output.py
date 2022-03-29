import asyncio
import logging

from aiohttp import ClientSession, ClientResponse
from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError
from time import time, time_ns


# https://docs.aiohttp.org/en/stable/client_quickstart.html
# https://docs.influxdata.com/influxdb/v2.1/api/#tag/Write
# https://docs.influxdata.com/influxdb/v2.1/write-data/developer-tools/api/


class InfluxDBOutput:
    host: str
    port: int
    org_name: str
    bucket: str
    api_token: str
    headers: dict

    session: ClientSession = ClientSession()

    buffer: str = ""
    buffer_size: int = 0

    write_interval = 5  # seconds

    write_task: asyncio.Task = None

    logger: logging.Logger

    timestamp_precision: str

    def __init__(self, host: str, port: int, org_name: str, bucket: str, api_token: str, ssl: bool = False,
                 timestamp_precision: str = "ms"):
        self.timestamp_precision = timestamp_precision
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.port = port
        self.org_name = org_name
        self.bucket = bucket
        self.api_token = api_token
        self.write_url = f"http{'s' if ssl else ''}://{self.host}:{self.port}/api/v2/write?" \
                         f"org={self.org_name}" \
                         f"&bucket={self.bucket}" \
                         f"&precision={self.timestamp_precision}"

        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json"
        }

    async def write_task_loop(self):
        """
        This loop runs as an asyncio.Task and makes a web request to InfluxDB every `self.write_interval` seconds
        """
        while True:

            # don't bother making a request if our buffer is empty
            if self.buffer_size == 0:
                await asyncio.sleep(1)
                continue

            write_success = False
            start = time()
            try:
                response: ClientResponse = await self.session.post(
                    self.write_url, data=self.buffer, headers=self.headers
                )
            except Exception as e:
                self.logger.info(e)
            else:
                if response.status == 204:
                    write_success = True
            finally:
                end = time()

            if write_success:
                delay_ms = round((end - start) * 1000, 1)
                self.logger.info(f"Wrote {self.buffer_size} lines to InfluxDB [{delay_ms}ms]")
                self.buffer = ""
                self.buffer_size = 0

            await asyncio.sleep(self.write_interval)

    async def input(self, output_string: str):
        """
        This method should be added as an output of a LineProtocolInput using its add_output function
        :param output_string: The line protocol string to be sent to influxDB
        """
        if not output_string.endswith("\n"):
            output_string += "\n"

        possible_timestamp_position = output_string.rfind(" ") + 1
        possible_timestamp = output_string[possible_timestamp_position:].strip("\n")
        has_timestamp = possible_timestamp.isdigit()

        if not has_timestamp:
            multiplier = \
                1/1_000_000_000 if self.timestamp_precision == "s" else \
                1/1_000_000 if self.timestamp_precision == "ms" else \
                1/1_000 if self.timestamp_precision == "us" else ''

            timestamp = round(time_ns() * multiplier)

            output_string += str(timestamp)

        # add string to buffer
        self.buffer += output_string
        # increment buffer size
        self.buffer_size += 1

        # start write task if not started already
        if not self.write_task:
            self.write_task = asyncio.create_task(self.write_task_loop())
