from logging import info

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ServerDisconnectedError
from time import time

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
    last_write: float = 0  # seconds

    buffer_write_timeout = 5  # seconds
    buffer_write_size = 1000  # samples

    def __init__(self, host: str, port: int, org_name: str, bucket: str, api_token: str, ssl: bool = False):
        self.host = host
        self.port = port
        self.org_name = org_name
        self.bucket = bucket
        self.api_token = api_token
        self.write_url = f"http{'s' if ssl else ''}://{self.host}:{self.port}/api/v2/write?" \
                         f"org={self.org_name}" \
                         f"&bucket={self.bucket}" \
                         f"&precision=ms"

        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json"
        }

    async def output(self, output_string: str):
        if not output_string.endswith("\n"):
            output_string += "\n"
        timeout_reached = time() - self.last_write > self.buffer_write_timeout
        buffer_full = self.buffer_size >= self.buffer_write_size
        if timeout_reached or buffer_full:
            try:
                await self.session.post(self.write_url, data=self.buffer, headers=self.headers)
            except Exception as e:
                info(e)
                info(f"Failed to write to InfluxDB. Adding to buffer [size {self.buffer_size}]")
                self.buffer += output_string
                self.buffer_size += 1
            else:
                info(f"Wrote to InfluxDB with buffer size {self.buffer_size}")
                self.last_write = time()
                self.buffer = ""
                self.buffer_size = 0
        else:
            self.buffer += output_string
            self.buffer_size += 1

