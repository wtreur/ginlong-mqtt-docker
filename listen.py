#!/usr/bin/env python3

import paho.mqtt.publish as publish
import socket
import binascii
import time
import sys
import string
import configparser
import io
import logging
from requests import post

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

configFile = "./config.ini"
logger.info('Reading config file: %s', configFile)

config = configparser.ConfigParser()
config.read(configFile)


###########################
# Variables

listen_address = config.get('solar_converter', 'listen_address')
listen_port = config.getint('solar_converter', 'listen_port')

mqtt_topic = config.get('mqtt', 'topic')
mqtt_server = config.get('mqtt', 'server')
mqtt_port = config.getint('mqtt', 'port')
mqtt_auth = None
if (config.getboolean('mqtt', 'auth')):
    mqtt_auth= {
        'username': config.get('mqtt', 'username'),
        'password': config.get('mqtt', 'password')
    }

mqtt_tls=None
if (config.getboolean('mqtt', 'tls')):
    mqtt_tls = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((listen_address, listen_port))
sock.listen(1)

while True: 
    logger.info('Waiting for a connection')
    conn,addr = sock.accept()
    try:
        rawdata = conn.recv(1000)
        hexdata = binascii.hexlify(rawdata)
        if(len(hexdata) == 276):
            timestamp = str(time.time_ns())
            messages = []
            states = {}
            serial = binascii.unhexlify(hexdata[30:60]).decode('ascii')
            
            logger.info('Hex data %s', hexdata)
            logger.info('Serial %s', serial)
            logger.info('Length %s', len(hexdata))

            # These values are not sent, but might be useful
            #
            # states["vpv1"] = float(int(hexdata[66:70],16))/10
            # states["vpv2"] = float(int(hexdata[70:74],16))/10
            # states["ipv1"] = float(int(hexdata[78:82],16))/10
            # states["ipv2"] = float(int(hexdata[82:86],16))/10
            # states["temp"] = float(int(hexdata[62:66],16))/10
            # states["kwhtoday"] = float(int(hexdata[138:142],16))/100
            # states["kwhthismonth"] = int(hexdata[174:178],16)

            states["output"] = float(int(hexdata[118:122],16))
            states["kwhtotal"] = float(int(hexdata[142:150],16))/10

            messages.append({
                'topic': mqtt_topic,
                'payload': 'solar-power,unit=kWh generated=%s %s' % (states["kwhtotal"], timestamp),
                'retain': False
            })

            messages.append({
                'topic': mqtt_topic,
                'payload': "solar-power,unit=W power=%s %s" % (states["output"], timestamp),
                'retain': False
            })

            logger.info('Sending to mqtt: %s', messages)
            print(publish.multiple(msgs=messages, hostname=mqtt_server, port=mqtt_port, auth=mqtt_auth, tls=mqtt_tls))

            if (config.has_section('hass')):
                print('[hass] config section found, sending sensor state')
                
                hass_url = config.get('hass', 'url')
                hass_token = config.get('hass', 'token')
                hass_sensor_generated = config.get('hass', 'sensor_generated')
                hass_sensor_power = config.get('hass', 'sensor_power')

                headers = {
                    "Authorization": 'Bearer %s' % hass_token,
                    "content-type": "application/json",
                }

                generated_sensor_state = {
                    'state': states["kwhtotal"],
                    'attributes': {
                        'unit_of_measurement': 'kWh',
                        'icon': 'mdi:solar-power'
                    }
                }
                power_sensor_state = {
                    'state': states["output"],
                    'attributes': {
                        'unit_of_measurement': 'W',
                        'icon': 'mdi:solar-power'
                    }
                }
                
                logger.info('posting sensor state %s to sensor %s...', generated_sensor_state, hass_sensor_generated)
                response = post('%s/api/states/%s' % (hass_url, hass_sensor_generated), headers=headers, json=generated_sensor_state, timeout=5)
                logger.info('response: %s', response.text)

                logger.info('posting sensor state %s to sensor %s...', power_sensor_state, hass_sensor_power)
                response = post('%s/api/states/%s' % (hass_url, hass_sensor_power), headers=headers, json=power_sensor_state, timeout=5)
                logger.info('response: %s', response.text)
            else:
                print('No hass config found, not posting sensor values.')

    finally:
        logger.info('Done')