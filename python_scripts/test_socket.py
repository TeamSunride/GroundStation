import socket
from time import sleep, time
from math import sin
TCP_IP = "127.0.0.1"
TCP_PORT = 8094

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while True:
    message = f"demo,device=sensorA value={sin(time()) * 100}\n"
    print(message)
    s.send(message.encode())
    sleep(0.01)