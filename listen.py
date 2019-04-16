#!/usr/bin/env python3

import paho.mqtt.publish as publish
import socket
import binascii
import time
import sys
import string
import configparser
import io
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

configFile = os.environ['SOLAR_INVERTER_LISTENER_CONFIG_FILE']
logger.info('Reading config file: %s', configFile)

config = configparser.ConfigParser()
config.read(configFile)


###########################
# Variables

listen_address = config['DEFAULT']['listen_address']
listen_port = int(config['DEFAULT']['listen_port'])
topic = config['MQTT']['topic']
mqtt_server = config['MQTT']['mqtt_server']
mqtt_port = int(config['MQTT']['mqtt_port'])

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
            states["kwhtotal"] = float(int(hexdata[146:150],16))/10

            messages.append({
                'topic': topic,
                'payload': 'solar-power,unit=kWh generated=%s %s' % (states["kwhtotal"], timestamp),
                'retain': False
            })

            messages.append({
                'topic': topic,
                'payload': "solar-power,unit=W power=%s %s" % (states["output"], timestamp),
                'retain': False
            })

            logger.info('Sending to mqtt: %s', messages)
            publish.multiple(messages)

    finally:
        logger.info('Done')