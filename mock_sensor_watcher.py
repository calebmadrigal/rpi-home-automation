#!/usr/bin/env python
#
# Raspberry Pi Home Security System - sensor_watcher

__author__ = "Caleb Madrigal"

import zmq
import time
import logging
import settings

# TODO: Daemonize process?
# TODO: Combine all logs into a single log?
LOG_FILE = "/var/log/homeautomation_sensor.log"

def door_sensor_callback(channel):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(settings.sensor_watcher_conn_str)
    socket.send_json({'command':'triggered'})
    logging.info("door was opened")

def run():
    # Input pin
    print "Setting pin {0} to watch for rising inputs".format(settings.door_sensor_pin)

    logging.info("sensor_watcher started; sensor_pin:{0}, bouncetime:{1}".format(
            settings.door_sensor_pin, settings.door_sensor_bounce_time))

    # TODO: See if this exits

    # Keep process alive
    while True:
        # TODO: Can probably make this a larger time, since it will be preempted by callback
        time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
    run()

