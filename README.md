# SunrIde Ground Station Software

In this project, Grafana and InfluxDB are combined to provide a great solution for data visualization and storage.


> [Grafana](https://grafana.com/grafana/) is a multi-platform open source analytics and interactive visualization web
> application. It provides charts, graphs, and alerts for the web when connected to supported data sources.
[_Wikipedia_](https://en.wikipedia.org/wiki/Grafana)

> [InfluxDB]() is an open-source time series database (TSDB) developed by the company InfluxData. It is written in the
> Go programming language for storage and retrieval of time series data in fields such as operations monitoring,
> application metrics, Internet of Things sensor data, and real-time analytics.
> [_Wikipedia_](https://en.wikipedia.org/wiki/InfluxDB)

Grafana and InfluxDB are hosted in [Docker Containers](https://www.docker.com/resources/what-container/), 
allowing them to run on most platforms with minimal environment setup/configuration. 
[Docker Compose](https://docs.docker.com/compose/) is used to run the containers together.

In order to stream data into Grafana and InfluxDB, we send strings of data over a Serial connection from an Arduino 
formatted as [InfluxDB Line Protocol](https://docs.influxdata.com/influxdb/v2.1/reference/syntax/line-protocol/). 
This is received by a python script, where the data is then sent to Grafana and InfluxDB.

[Grafana Live](https://grafana.com/docs/grafana/latest/live/) is a new feature in Grafana which allows data to be 
pushed to the frontend as soon as it occurs. WebSockets are used for this, and it allows us to display real-time graphs 
of our data on Grafana's dashboards. However, Grafana is not a database. It does not store data. And if the live data 
stream is interrupted, we will lose data. Therefore, we need to use a database such as InfluxDB.

The python script streams data to Grafana over a WebSocket connection, and writes data to InfluxDB in batches. This is 
because InfluxDB offers an HTTP API rather than WebSockets, so sending a separate request for each data point would be 
inefficient.

## System Architecture Diagram

![img.png](images/ground_station_diagram.png)

