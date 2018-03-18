# Ginlong Solar Inverter Collector

_Based on [dpoulson/ginlong-mqtt](https://github.com/dpoulson/ginlong-mqtt)_

Script that listens to messages from a Ginlong Solor Inverter and pushes it to MQTT

Tested with `Solis-1P3K-4G` on firmware `H4.01.51Y4.0.02W1.0.57(2017-12-211-D)`

## Usage
1. Setup an MQTT server
1. Update `config.ini` with the right values for your system
1. Run `./listen.py`
1. Go to the Ginlong web interface and setup remote server to the host running the script.
1. Messages should start rolling in every 7 minutes or so

## MQTT topics / state
The following topics / states will be used. Whereas `client_id` is set in `config.ini` and `inverter_serial` can be found in the Ginlong web interface

- `client_id/inverter_serial/vpv1`
- `client_id/inverter_serial/vpv2`
- `client_id/inverter_serial/ipv1`
- `client_id/inverter_serial/ipv2`
- `client_id/inverter_serial/output`
- `client_id/inverter_serial/temp`
- `client_id/inverter_serial/kwhtoday`
- `client_id/inverter_serial/kwhthismonth`
- `client_id/inverter_serial/kwhtotal`

## Daemon installation
1. Create user: `sudo adduser --system --home /srv/solar-inverter solar-inverter`
1. Install requirements: `sudo -H -u solar-inverter pip install paho-mqtt`
1. Copy contents of dir to `/src/solar-inverter`
1. Ensure `config.ini` is valid
1. Copy `solar-inverter-listener.service` to `/etc/systemd/system/solar-inverter-listener.service`
1. Enable with `sudo systemctl enable solar-inverter-listener.service`
1. Debug with `sudo journalctl -f -u solar-inverter-listener.service`