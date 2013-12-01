#!/usr/bin/env python
#
# Raspberry Pi Home Security System - gpio_helper

__author__ = "Caleb Madrigal"

import zmq
import time
import logging
import settings
from common import setup_logger
try:
    import RPi.GPIO as GPIO
except ImportError:
    import gpio_mock as GPIO


logger = setup_logger("gpio", settings.gpio_log_file, logging.DEBUG)


def pulse_pin(pin, pulse_time_in_secs=1.5):
    GPIO.output(pin, True)
    time.sleep(pulse_time_in_secs)
    GPIO.output(pin, False)


def setup_switch_gpio_pins():
    # Setup modes for GPIO pins
    GPIO.setmode(GPIO.BCM)

    logger.info("Switch on pins: {0}".format(settings.on_pins))
    logger.info("Switch off pins: {0}".format(settings.off_pins))

    # Output pins
    for pin in settings.on_pins + settings.off_pins:
        GPIO.setup(pin, GPIO.OUT)


def setup_sensor_callback(sensor_callback):
    # Setup modes for GPIO pins
    GPIO.setmode(GPIO.BCM)

    logger.info("Door sensor pin: {0}, bounce time: {1}".
                format(settings.door_sensor_pin, settings.door_sensor_bounce_time))

    # Input pin
    GPIO.setup(settings.door_sensor_pin, GPIO.IN)
    GPIO.add_event_detect(settings.door_sensor_pin, GPIO.RISING,
                          callback=sensor_callback,
                          bouncetime=settings.door_sensor_bounce_time)


def run():
    logger.info("GPIO Helper started")

    setup_switch_gpio_pins()

    context = zmq.Context()
    task_queue = context.socket(zmq.PULL)
    task_queue.bind(settings.switch_worker_conn_str)

    while True:
        msg = task_queue.recv_json() # Blocking call
        pin = msg['pin']
        pulse_pin(pin, settings.switch_pulse_time_in_secs)
        logger.debug("Pulsing pin: {0}".format(pin))

if __name__ == "__main__":
    run()
