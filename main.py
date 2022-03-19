from gs_server.serial import SerialLineProtocolInput
import asyncio


async def my_output(output_str: str):
    print(output_str)


serial_input = SerialLineProtocolInput("COM4", 9600)
serial_input.add_output(my_output)

loop = asyncio.get_event_loop()
loop.create_task(serial_input.connect())
loop.run_forever()
