import coloredlogs, logging

coloredlogs.install()  # colourful logging in the terminal

from .grafana_websocket_output import *
from .influxdb_output import *
from .serial_input import *
