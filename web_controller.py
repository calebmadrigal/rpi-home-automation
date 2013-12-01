#!/usr/bin/env python
#
# Raspberry Pi Home Security System - web_controller

__author__ = "Caleb Madrigal"

import zmq
import settings
import logging
from common import setup_logger
from flask import Flask, request
from flask.ext.restful import Resource, Api

logger = setup_logger("web", settings.web_log_file, logging.DEBUG)

############################################################################ Interaction with master


def send_recv_message(json_msg):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(settings.web_controller_conn_str)
    socket.send_json(json_msg)
    return socket.recv_json()


def set_switch(switch_id, switch_value):
    logger.info("Request master set switch {0} to {1}".format(switch_id, switch_value))
    state = send_recv_message({'command':'set_switch', 'switch_id':switch_id, 'value':switch_value})
    return state


def set_all_switches(switch_value):
    logger.info("Request master set all to {0}".format(switch_value))
    state = send_recv_message({'command':'set_all', 'value':switch_value})
    return state


def set_automation_mode(automation_mode_value):
    logger.info("Request master set automation mode to {0}".format(automation_mode_value))
    state = send_recv_message({'command':'set_automation_mode', 'value':automation_mode_value})
    return state


def get_state():
    logger.debug("Get state")
    state = send_recv_message({'command':'get_state'})
    return state

# TODO: add alarm:on, alarm:off

############################################################################################ Classes


class StateController(Resource):
    def get(self):
        state = get_state()
        return state


class AutomationModeController(Resource):
    def get(self):
        state = get_state()
        return {'automation_mode': state['automation_mode']}

    def put(self):
        automation_mode_value = request.form['value'].lower()
        if automation_mode_value in ['on', 'off']:
            state = set_automation_mode(automation_mode_value)
            return state, 200
        else:
            return {'error': 'Automation mode must be on or off'}, 400


class AllController(Resource):
    def put(self, switch_value):
        switch_value = switch_value.lower()
        if switch_value in ['on', 'off']:
            state = set_all_switches(switch_value)
            return state, 200
        else:
            return {'error': 'Switch value must be on or off'}, 400


class SwitchController(Resource):
    def get(self, switch_id):
        switch_id = switch_id.lower()
        state = get_state()
        if switch_id == 'list' or switch_id == 'all':
            return state['switches']
        if switch_id in state['switches']:
            return {switch_id: state['switches'][switch_id]}
        else:
            return {'error': 'Invalid switch name'}, 400

    def put(self, switch_id):
        switch_id = switch_id.lower()
        switch_value = request.form['value'].lower()

        if switch_id not in settings.switches:
            valid_switches = ','.join(settings.switches)
            return {'error': 'Invalid switch number - must be one of these: '+valid_switches}, 400
        elif switch_value not in ['on', 'off']:
            return {'error': 'Invalid switch value - must be on or off'}, 400
        else:
            state = set_switch(switch_id, switch_value)
            return state, 200

####################################################################################### RESTful API

# Setup RESTful API
app = Flask(__name__)
api = Api(app)
api.add_resource(StateController, '/state/')
api.add_resource(AutomationModeController, '/automation_mode/')
api.add_resource(AllController, '/all/<string:switch_value>')
api.add_resource(SwitchController, '/switch/<string:switch_id>')

@app.route('/')
def main_page():
    with open(settings.index_page_file, "r") as page:
        return page.read()


def run():
    logger.info("Web controller started - serving on {0}:{1}".format(settings.hostname, settings.port))
    app.run(host=settings.hostname, port=settings.port, debug=False)

if __name__ == '__main__':
    run()
