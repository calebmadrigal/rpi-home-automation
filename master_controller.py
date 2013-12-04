#!/usr/bin/env python
#
# Raspberry Pi Home Security System - master_controller

__author__ = "Caleb Madrigal"

import time
import json
import zmq
import logging
import datetime
import smtplib
import settings
import gpio_helper
from common import setup_logger

logger = setup_logger("master", settings.master_log_file, logging.DEBUG)

######################################################################################### State file


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

def load_email_credentials():
    credentials = {}
    with open('credentials.json', 'r') as f:
        credentials = json.loads(f.read())
    return credentials

############################################################################# gpio_helper interface


def set_switch(switch_id, switch_value):
    logger.debug("Setting switch {0} to {1}".format(switch_id, switch_value))
    # Determine pin number to pulse
    pin = 0
    switch_index = settings.switches.index(switch_id)
    if switch_index != -1:
        if switch_value == 'on':
            pin = settings.on_pins[switch_index]
        else:
            pin = settings.off_pins[switch_index]

    # Send pulse request to switch_worker
    context = zmq.Context()
    switch_socket = context.socket(zmq.PUSH)
    switch_socket.connect(settings.switch_worker_conn_str)
    switch_socket.send_json({'pin':pin})

################################################################################### Alarm functions


def sound_alarm(state):
    for switch_id in settings.switches:
        set_switch(switch_id, 'on')
    time.sleep(20)
    for switch_id in settings.switches:
        set_switch(switch_id, 'off')

########################################################################## Web controller interface


def handle_web_req(web_socket, state):
    msg = web_socket.recv_json()
    logger.debug("Request from web: {0}".format(msg))

    command = msg['command']
    if command == 'set_switch':
        switch_id = msg['switch_id']
        switch_value = msg['value']
        set_switch(switch_id, switch_value)
        state['switches'][switch_id] = switch_value
        save_state(state)
    elif command == 'set_all':
        switch_value = msg['value']
        logger.debug("Setting all to {0}".format(switch_value))
        for switch_id in state['switches'].keys():
            set_switch(switch_id, switch_value)
            state['switches'][switch_id] = switch_value
        save_state(state)
    elif command == 'set_automation_mode':
        state['automation_mode'] = msg['value']
        logger.debug("Setting automation mode to {0}".format(msg['value']))
        save_state(state)

    # No matter what, return the state (including if the command is 'get_state')
    web_socket.send_json(state)

    return state

#################################################################################### Alarm handling


class AlarmControl:
    def __init__(self, state, alarm_duration, email_username, email_password):
        self.state = state
        self.alarm_duration = alarm_duration
        self.email_username = email_username
        self.email_password = email_password
        self.alarm_sounding = False
        self.alarm_start_time = ""

    def start_alarm(self):
        if self.alarm_sounding:
            return

        logger.info("Starting alarm")
        self.alarm_sounding = True
        self.alarm_start_time = datetime.datetime.now()
        self.perform_alarm()

    def stop_alarm(self):
        logger.info("Stopping alarm")
        self.alarm_sounding = False

        # Turn all switches off
        for switch_id in settings.switches:
            set_switch(switch_id, 'off')
            self.state['switches'][switch_id] = 'off'

    def process(self):
        if self.alarm_sounding:
            logger.debug("Alarm still on")
            now = datetime.datetime.now()
            seconds_since_alarm = (now - self.alarm_start_time).seconds
            if seconds_since_alarm > self.alarm_duration:
                self.stop_alarm()

    def perform_alarm(self):
        logger.debug("Perform alarm!!!")

        # Turn all switches on
        for switch_id in settings.switches:
            set_switch(switch_id, 'on')
            self.state['switches'][switch_id] = 'on'

        # Send alert email
        self.send_alert_email()

    def send_alert_email(self):
        email_from = 'alarmrobot@yahoo.com'
        email_to  = 'trigger@ifttt.com'
        subj='#alarmtriggered Alarm triggered'
        date='12/3/2013'
        message_text='The door was opened.'
        msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % ( email_from, email_to, subj, date, message_text )

        try:
            server = smtplib.SMTP("smtp.mail.yahoo.com",587)
            server.login(self.email_username, self.email_password)
            server.sendmail(email_from, email_to, msg)
            server.quit()
            logger.debug("Successfully sent alart email")
        except Exception, e:
            logger.debug("failed to send alart email")

############################################################################################### Run


def run():
    logger.info("Master started")

    # Read state from file (or create initial state file)
    state = read_state()

    # Set switches the the appropriate values (needed if the power went out)
    for switch_id in state['switches'].keys():
        switch_value = state['switches'][switch_id]
        set_switch(switch_id, switch_value)
        logging.info("Setting switch {0} to init value of {1}".format(switch_id, switch_value))

    # Setup web and sensor sockets
    context = zmq.Context()
    web_socket = context.socket(zmq.REP)
    web_socket.bind(settings.web_controller_conn_str)

    poll = zmq.Poller()
    poll.register(web_socket, zmq.POLLIN)

    credentials = load_email_credentials()
    email_un = credentials['email_username']
    email_pw = credentials['email_password']

    alarm_control = AlarmControl(state, settings.alarm_duration, email_un, email_pw)

    def alarm_callback(channel_unused):
        alarm_control.start_alarm()

    gpio_helper.setup_sensor_callback(alarm_callback)

    # Main control loop
    while True:
        poll_result = dict(poll.poll(timeout=1000))  # Wait up to 1 second

        # Handle requests from web controller
        if (web_socket in poll_result) and (poll_result[web_socket] == zmq.POLLIN):
            state = handle_web_req(web_socket, state)
            alarm_callback(None)

        # Do any necessary alarm-related work
        alarm_control.process()

if __name__ == '__main__':
    run()
