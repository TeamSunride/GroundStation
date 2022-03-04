# SunrIde GroundStation

## Ground Station Setup and Documentation:

This installation guide assumes the ground station is run on a debian based system.

run ```cat /etc/os-release``` in the terminal to check.

Next, run ```which docker``` to check if docker is installed.

If Docker is not installed, it will need to be installed.

run the following commands for the straightforward installation:

> This installed **stable** Docker version using this method is likely a few months out of date. This should not affect the Ground Station setup.

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
```
```sudo apt-get upgrade``` may be run but it may take time to upgrade depending on the Operating System state.

Otherwise, follow the instructions in the following links to install the Docker Engine and Docker-Compose.

> RECOMMENDATION: On Raspberry Pi, install the 64bit version of Docker under the Debian install section if the raspbian version installed is 64bit (See command above to check Operating System).

https://docs.docker.com/engine/install/
https://docs.docker.com/compose/install/

### Spin Up Containers:

To spin up containers, clone this directory using:

```bash
git clone https://github.com/TeamSunride/GroundStation.git
```

cd into the directory and run the containers:

```bash
cd GroundStation
sudo docker-compose up -d
```

This will spin up the containers detailed in the ```docker-compose.yml``` file in the root directory.

To check the status of the Docker containers after spinning up the containers, run:

```bash
sudo docker ps -a
```

To access the services that have been spun up, navigate to the IP address of the Docker host and append the port number of the service to the IP address.

```
<IP-address>:<Port>

Example:
192.168.1.5:3000
```

To find the host IP address, run ```ip a```. The main network device is likely to be the second device in the list after the loopback device with IP ```127.0.0.1```.

The port mappings for the services can be found in the ```docker-compose.yml``` and below for convenience.

| Service     | Port        |
| ----------- | ----------- |
| Grafana     | 3000        |
| InfluxDB    | 8086        |

Grafana and InfluxDB have been already configured with a username and password:

| Service     | Username    | Password    |
| ----------- | ----------- | ----------- |
| Grafana     | admin       | sunride     |
| InfluxDB    | sunride     | telemetry   |

### Other Things to Note

- Telegraf is configured entirely from its config file. See the ```telegraf_doc.conf``` for examples on how to change the setup for telegraf.