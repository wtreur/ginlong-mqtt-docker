#!/usr/bin/env python

import paho.mqtt.publish as publish
import socket
import binascii
import time
import sys
import string
import ConfigParser
import io
import json


with open("config.ini") as f:
        sample_config = f.read()
config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))


###########################
# Variables

listen_address = config.get('DEFAULT', 'listen_address')
listen_port = int(config.get('DEFAULT', 'listen_port'))
client_id = config.get('MQTT', 'client_id')
mqtt_server = config.get('MQTT', 'mqtt_server')
mqtt_port = int(config.get('MQTT', 'mqtt_port'))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((listen_address, listen_port))
sock.listen(1)

while True: 
    if __debug__:
        print 'waiting for a connection'
    conn,addr = sock.accept()
    try:
        rawdata = conn.recv(1000)
        hexdata = binascii.hexlify(rawdata)

        if(len(hexdata) == 276):
            timestamp = (time.strftime("%F %H:%M"))
            messages = []
            states = {}
            serial = binascii.unhexlify(str(hexdata[30:60]))
            if __debug__:
                print 'Hex data: %s' % hexdata
                print 'Serial %s' % serial
                print 'Length %s' % len(hexdata)
            topic = client_id + '/' + serial + '/'

            states["vpv1"] = float(int(hexdata[66:70],16))/10
            states["vpv2"] = float(int(hexdata[70:74],16))/10
            states["ipv1"] = float(int(hexdata[78:82],16))/10
            states["ipv2"] = float(int(hexdata[82:86],16))/10
            states["output"] = float(int(hexdata[238:242],16) + int(hexdata[242:246],16))/10
            states["temp"] = float(int(hexdata[62:66],16))/10
            states["kwhtoday"] = float(int(hexdata[138:142],16))/100
            states["kwhthismonth"] = int(hexdata[174:178],16)
            states["kwhtotal"] = float(int(hexdata[146:150],16))/10

            for state, value in states.items():
                messages.append({
                    'topic': topic + state,
                    'payload': value,
                    'retain': False
                })

            publish.multiple(messages)

    finally:
        if __debug__:
            print "Finally"