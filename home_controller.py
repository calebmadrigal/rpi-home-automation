#!/usr/bin/env python
#
# Raspberry Pi Control system for home automation.

from flask import Flask, request
from flask.ext.restful import Resource, Api
from time import sleep
from Queue import Queue
from threading import Thread
import RPi.GPIO as GPIO

########################################################################################## Constants

# Format of file: 1=on\n2=off\n3=off (meaning switch 1 on, switch 2 and 3 off)
switch_values_file = "/home/pi/rpi-home-automation/switch_values.dat"

# Index page
index_page_file = "/home/pi/rpi-home-automation/index.html"

# Automation mode
automation_mode = 'off'

# Switch data
switch_options = ['on', 'off']
switches = ['1', '2', '3']

# Actuator pin data
on_pins = [9, 1, 7]
off_pins = [11, 0, 8]

# Door sensor data
door_sensor_pin = 24
alarm_time_on = 5 #seconds
door_sensor_bounce_time = 34 * 60 * 1000 # 34 min
door_sensor_triggered = False


########################################################################################## Functions

def door_sensor_callback(channel):
    global door_sensor_triggered
    door_sensor_triggered = True
    print "Door sensor triggered"

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

def set_and_save_switch(switch_num, switch_value):
    update_switch_value(switch_num, switch_value)
    set_switch(switch_num, switch_value)

def set_all(value):
    write_switch_data({switch_num:value for switch_num in switches})
    for switch_num in switches:
        set_switch(switch_num, value)

def set_switches_from_file():
    switch_dict = read_switch_data()
    for (switch_num, switch_value) in switch_dict.items():
        set_switch(switch_num, switch_value)

############################################################################################# Classes

class AutomationModeController(Resource):
    def put(self, automation_mode_value):
        print "Setting automation mode =", automation_mode_value
        global automation_mode
        automation_mode = automation_mode_value
        return {'automation': automation_mode}, 201

class AutomationModeReaderController(Resource):
    def get(self):
        global automation_mode
        return {'automation': automation_mode}, 200

class AllController(Resource):
    def put(self, switch_value):
        if switch_value in switch_options:
            set_all(switch_value)
            return read_switch_data(), 201
        else:
            return {'error': 'Switch value must be on or off'}, 400

class SwitchList(Resource):
    def get(self):
        return read_switch_data()

class SwitchController(Resource):
    def get(self, switch_num):
        if switch_num in switches:
            return {switch_num: read_switch_value(switch_num)}
        else:
            return {'error': 'Invalid switch number'}, 400

    def put(self, switch_num):
        switch_value = request.form['value']

        if switch_num not in switches:
            valid_switches = ','.join(switches)
            return {'error': 'Invalid switch number - must be one of these: '+valid_switches}, 400
        elif switch_value not in switch_options:
            return {'error': 'Invalid switch value - must be on or off'}, 400
        else:
            set_and_save_switch(switch_num, switch_value)
            return {switch_num: switch_value}, 201


######################################################################################## RESTful API

# Setup modes for GPIO pins
GPIO.setmode(GPIO.BCM)

# Output pins
for pin in on_pins + off_pins:
    GPIO.setup(pin, GPIO.OUT)

# Input pin
GPIO.setup(door_sensor_pin, GPIO.IN)
GPIO.add_event_detect(door_sensor_pin, GPIO.RISING, \
                      callback=door_sensor_callback, bouncetime=door_sensor_bounce_time)

# Setup RESTful API
app = Flask(__name__)
api = Api(app)
api.add_resource(AllController, '/all/<string:switch_value>')
api.add_resource(SwitchList, '/switch/list')
api.add_resource(SwitchController, '/switch/<string:switch_num>')
api.add_resource(AutomationModeController, '/automation/<string:automation_mode_value>')
api.add_resource(AutomationModeReaderController, '/automation/mode')

@app.route('/')
def main_page():
    with open(index_page_file, "r") as page:
        return page.read()


#################################################################################### Trigger watcher
def sound_alarm():
    # For now, just turn everything on... later, we will really sound the alarm :)
    print "ALERT!!! ALERT!!! ALERT!!!"
    set_all('on')
    sleep(30)
    set_all('off')

def automated_controller():
    global door_sensor_triggered
    global mode

    while True:
        if door_sensor_triggered:
            door_sensor_triggered = False

            print "Automation mode:", automation_mode
            if automation_mode == 'on':
                sound_alarm()
        else:
            sleep(0.1)


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

    # Run web app and web api
    print "Running web server"
    app.run(host='0.0.0.0', port=80, debug=True)

    automation_thread.join()
