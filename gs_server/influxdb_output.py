from aioinflux import InfluxDBClient

# refer to https://www.scivision.dev/python-windows-visual-c-14-required


class InfluxDBOutput:
    host: str
    port: int
    db: str

    client: InfluxDBClient

    def __init__(self, host: str, port: int, **kwargs):
        self.host = host
        self.port = port

        self.client = InfluxDBClient(
            host=self.host,
            port=self.port,
            **kwargs
        )

    async def output(self, output_string: str):
        await self.client.write(output_string)

