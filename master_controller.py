#!/usr/bin/env python
#
# Raspberry Pi Home Security System - master_controller

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

import time
import json
import zmq
import settings
import gpio_helper


######################################################################################### state file


def build_init_state():
    state = {'automation_mode': 'off', 'switches': {}}
    for switch_id in settings.switches:
        state['switches'][switch_id] = 'off'
    return state


def save_state(state):
    with open(settings.state_file, 'w') as f:
        f.write(json.dumps(state))


def read_state():
    state = build_init_state()
    try:
        with open(settings.state_file, 'r') as f:
            state = json.loads(f.read())
    except Exception, e:
        # Go with default state
        pass
    return state

############################################################################ switch_worker interface


def set_switch(switch_id, switch_value):
    # Determine pin number to pulse
    pin = 0
    switch_index = settings.switches.index(switch_id)
    if switch_index != -1:
        if switch_value == 'on':
            pin = settings.on_pins[switch_index]
        else:
            pin = settings.off_pins[switch_index]

    # TODO: Offload determining which pin to pulse to switch_worker?

    # Send pulse request to switch_worker
    context = zmq.Context()
    switch_socket = context.socket(zmq.PUSH)
    switch_socket.connect(settings.switch_worker_conn_str)
    switch_socket.send_json({'pin':pin})

#################################################################################### Alarm functions


def sound_alarm(state):
    print "ALERT!!! ALERT!!! ALERT!!!"
    for switch_id in settings.switches:
        set_switch(switch_id, 'on')
    time.sleep(20)
    for switch_id in settings.switches:
        set_switch(switch_id, 'off')


def handle_web_req(web_socket, state):
    msg = web_socket.recv_json()
    command = msg['command']
    if command == 'set_switch':
        switch_id = msg['switch_id']
        switch_value = msg['value']
        set_switch(switch_id, switch_value)
        state['switches'][switch_id] = switch_value
        save_state(state)
    elif command == 'set_all':
        switch_value = msg['value']
        for switch_id in state['switches'].keys():
            set_switch(switch_id, switch_value)
            state['switches'][switch_id] = switch_value
        save_state(state)
    elif command == 'set_automation_mode':
        state['automation_mode'] = msg['value']
        save_state(state)

    # No matter what, return the state (including if the command is 'get_state')
    web_socket.send_json(state)

    return state


def run():
    # Read state from file (or create initial state file)
    state = read_state()

    # Set switches the the appropriate values (needed if the power went out)
    for switch_id in state['switches'].keys():
        switch_value = state['switches'][switch_id]
        set_switch(switch_id, switch_value)

    # Setup web and sensor sockets
    context = zmq.Context()
    web_socket = context.socket(zmq.REP)
    web_socket.bind(settings.web_controller_conn_str)

    # TODO: Make sure poll() is non-blocking so that we can control the alarm sounding length
    poll = zmq.Poller()
    poll.register(web_socket, zmq.POLLIN)

    # Variables to control how long we sound the alarm; note that I made these variables
    # into a dict so that triggered could be set in the alarm_callback closure.
    alarm_data = dict(triggered=False, alarm_sounding=False, alarm_start_time="")

    def alarm_callback(channel):
        alarm_data['triggered'] = True

    gpio_helper.setup_sensor_callback(alarm_callback)

    # Main control loop
    while True:
        poll_result = dict(poll.poll(timeout=1000))  # Wait up to 1 second

        if (web_socket in poll_result) and (poll_result[web_socket] == zmq.POLLIN):
            state = handle_web_req(web_socket, state)

        if alarm_data['triggered']:
            alarm_data['triggered'] = False
            alarm_data['alarm_sounding'] = True
            print "Alarm triggered!"


if __name__ == '__main__':
    run()
