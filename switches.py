#!/usr/bin/env python
#
# Raspberry Pi Control system for home automation.

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

from time import sleep
from Queue import Queue
from threading import Thread
import RPi.GPIO as GPIO

########################################################################################## Actuators

def pulse_pin(pin, pulse_time_in_secs=1.5):
    print "Pulsing pin", pin
    GPIO.output(pin, True)
    sleep(pulse_time_in_secs)
    GPIO.output(pin, False)

def queue_pulse_pin(pin):
    pulse_queue.put(pin, block=False)

def set_switch(switch_num, value):
    """ Value must be 'on' or 'off'. """

    switch_index = switches.index(switch_num)
    if value == 'on':
        queue_pulse_pin(on_pins[switch_index])
    elif value == 'off':
        queue_pulse_pin(off_pins[switch_index])


############################################################## Reading/writing switch values to disk
def read_switch_data():
    with open(switch_values_file, "r") as f:
        lines = f.readlines()
        switch_data_list = [line.split('=') for line in lines]
        switch_data_list_cleaned = [(k.strip(), v.strip()) for (k,v) in switch_data_list]
    return dict(switch_data_list_cleaned)

def read_switch_value(switch_num):
    switch_dict = read_switch_data()
    return switch_dict[switch_num]

def write_switch_data(switch_dict):
    with open(switch_values_file, "w") as f:
        for (k,v) in switch_dict.items():
            f.write("{0}={1}\n".format(k,v))

def update_switch_value(switch_num, switch_value):
    switch_dict = read_switch_data()
    switch_dict[switch_num] = switch_value
    write_switch_data(switch_dict)

def set_switches_from_file():
    switch_dict = read_switch_data()
    for (switch_num, switch_value) in switch_dict.items():
        set_switch(switch_num, switch_value)

############################################################## Set and save switch values
def set_and_save_switch(switch_num, switch_value):
    update_switch_value(switch_num, switch_value)
    set_switch(switch_num, switch_value)

def set_all(value):
    write_switch_data({switch_num:value for switch_num in switches})
    for switch_num in switches:
        set_switch(switch_num, value)

#################################################################################### Initialize pins

def setup_gpio_pins():
    # Setup modes for GPIO pins
    GPIO.setmode(GPIO.BCM)

    # Output pins
    for pin in on_pins + off_pins:
        GPIO.setup(pin, GPIO.OUT)

    # Input pin
    GPIO.setup(door_sensor_pin, GPIO.IN)
    GPIO.add_event_detect(door_sensor_pin, GPIO.RISING, \
                          callback=door_sensor_callback, bouncetime=door_sensor_bounce_time)


###################################################################################### Worker thread
pulse_queue = Queue()

def pulser_worker():
    while True:
        pin = pulse_queue.get()
        pulse_pin(pin)
        pulse_queue.task_done()

if __name__ == '__main__':
    # Read data file and set switches accordingly.
    print "Setting initial switch values"
    set_switches_from_file()

    # Actuator worker thread
    print "Spawning actuator thread"
    actuator_thread = Thread(target=pulser_worker)
    actuator_thread.daemon = True
    actuator_thread.start()
    pulse_queue.join()

    # Automation thread
    print "Spawning automation thread"
    automation_thread = Thread(target=automated_controller)
    automation_thread.daemon = True
    automation_thread.start()

    automation_thread.join()
