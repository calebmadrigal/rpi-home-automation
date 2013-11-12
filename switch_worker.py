#!/usr/bin/env python
#
# Raspberry Pi Control system for home automation.

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

import zmq
import logging
import RPi.GPIO as GPIO
from time import sleep
import settings

########################################################################################## Actuators

def pulse_pin(pin, pulse_time_in_secs=1.5):
    print "Pulsing pin", pin
    GPIO.output(pin, True)
    sleep(pulse_time_in_secs)
    GPIO.output(pin, False)

def setup_switch_gpio_pins():
    # Setup modes for GPIO pins
    GPIO.setmode(GPIO.BCM)

    # Output pins
    for pin in on_pins + off_pins:
        GPIO.setup(pin, GPIO.OUT)

def run():
    context = zmq.Context()
    task_queue = context.socket(zmq.PULL)
    task_queue.bind("tcp://127.0.0.1:"+settings.switch_worker_port)

    while True:
        pin = task_queue.recv()
        pulse_pin(pin, settings.switch_pulse_time_in_secs)

if __name__ == "__main__":
    setup_switch_gpio_pins()
    run()

