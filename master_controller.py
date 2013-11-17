#!/usr/bin/env python
#
# Raspberry Pi Home Security System - master_controller

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

import time
import json
import zmq
import settings

######################################################################################### state file
def build_init_state():
    state = {'automation_mode': 'off', 'switches': {}}
    for switch_id in settings.switches:
        state['switches'][switch_id] = 'off'
    return state

def save_state(state):
    with open(settings.state_file, 'w') as f:
        f.write(json.dumps(state))

def read_state(state):
    state = build_init_state()
    with open(settings.state_file, 'r') as f:
        state = json.loads(f.read())
    return state

####################################################################################################

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

########################################################################### web_controller interface
########################################################################### sensor_watcher interface
############################################################################ switch_worker interface



#################################################################################### Alarm functions
def sound_alarm():
    print "ALERT!!! ALERT!!! ALERT!!!"
    set_all('on')
    time.sleep(20)
    set_all('off')

################################################################################ master_control_loop
def master_control_loop():
    context = zmq.Context()

    web_socket = context.socket(zmq.REP)
    web_socket.bind(settings.web_controller_conn_str)
    sensor_socket = context.socket(zmq.PULL)
    sensor_socket.bind(settings.sensor_watcher_conn_str)

    # TODO: Make sure poll() is non-blocking so that we can control the alarm sounding length
    poll = zmq.Poller()
    poll.register(web_socket, zmq.POLLIN)
    poll.register(sensor_socket, zmq.POLLIN)

    # Variables to control how long we sound the alarm
    alarm_is_sounding = False
    alarm_start_time = ""

    while True:
        poll_result = dict(poll.poll())
        if (web_socket in poll_result) and (poll_result[web_watcher] == zmq.POLLIN):
            handle_web_req(web_watcher)
        elif (sensor_socket in poll_result) and (poll_result[sensor_watcher] == zmq.POLLIN):
            handle_sensor_req(sensor_watcher)

        else:
            sleep(0.1)

if __name__ == '__main__':
    # TODO: Make supervisord start all of the processes?

    # Start switch_worker process
    # Start sensor_watcher process
    # Start web_controller process

    # Read data file and set switches accordingly.
    set_switches_from_file()

    master_control_loop()

