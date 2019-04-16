# Ginlong Solar Inverter Collector

_Based on [dpoulson/ginlong-mqtt](https://github.com/dpoulson/ginlong-mqtt)_

Script that listens to messages from a Ginlong Solor Inverter and pushes it to MQTT

Tested with `Solis-1P3K-4G` on firmware `H4.01.51Y4.0.02W1.0.57(2017-12-211-D)`

## Usage with docker-compose
1. Ensure docker and docker-compose
1. Copy `config.ini.sample` to `config.ini` and set the right values for your system
1. Run `docker-compose up`
1. Go to the Ginlong web interface and setup remote server to the docker host
1. Messages should start rolling in every 7 minutes or so

## Influx line format
These message using [influx line format](https://docs.influxdata.com/influxdb/v1.7/write_protocols/line_protocol_tutorial/) will be published on the topic set in `config.ini`. 
```
solar-power,unit=kWh generated=<<kwhtotal>> <<timestamp>>
solar-power,unit=W power=<<power>> <<timestamp>>
```