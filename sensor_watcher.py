#!/usr/bin/env python
#
# Raspberry Pi Control system for home automation.

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

import zmq
import time
import logging
import RPi.GPIO as GPIO
import settings

# TODO: Daemonize process?
# TODO: Combine all logs into a single log?
LOG_FILE = "/var/log/homeautomation_sensor.log"

def door_sensor_callback(channel):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.send("door:triggered")
    logging.info("door was opened")

def run():
    # Setup modes for GPIO pins
    GPIO.setmode(GPIO.BCM)

    # Input pin
    GPIO.setup(settings.door_sensor_pin, GPIO.IN)
    GPIO.add_event_detect(settings.door_sensor_pin, GPIO.RISING, \
                          callback=door_sensor_callback, \
                          bouncetime=settings.door_sensor_bounce_time)
    logging.info("sensor_watcher up; gpio:{0}, bouncetime:{1}".format(settings.door_sensor_pin,
                                                               settings.door_sensor_bounce_time)

    # TODO: See if this exits

    # Keep process alive
    while True:
        time.sleep(0.1)

if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
    run()

