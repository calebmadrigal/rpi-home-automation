#!/usr/bin/env python
#
# Raspberry Pi Home Security System - switch_worker

__author__ = "Caleb Madrigal"

import zmq
import time
import logging
import settings

LOG_FILE = "/var/log/homeautomation_switch.log"

########################################################################################## Actuators

def pulse_pin(pin, pulse_time_in_secs=1.5):
    print "Setting pin {0} to {1}".format(pin, 'True')
    time.sleep(pulse_time_in_secs)
    print "Setting pin {0} to {1}".format(pin, 'False')


def setup_switch_gpio_pins():
    # Output pins
    for pin in settings.on_pins + settings.off_pins:
        print "Setting pin {0} to GPIO.OUT".format(pin)

def run():
    context = zmq.Context()
    task_queue = context.socket(zmq.PULL)
    task_queue.bind(settings.switch_worker_conn_str)
    logging.info("switch_worker started")

    while True:
        msg = task_queue.recv_json() # Blocking call
        pin = msg['pin']
        pulse_pin(pin, settings.switch_pulse_time_in_secs)
        print "Pulsing pin", pin # TODO: Remove print line
        logging.info("Pulsing pin: {0}".format(pin))

if __name__ == "__main__":
    logging.basicConfig(filename=LOG_FILE, format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)
    logging.info("Off pins: {0}, On pins: {1}".format(settings.off_pins, settings.on_pins))
    setup_switch_gpio_pins()
    run()

