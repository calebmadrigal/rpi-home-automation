#!/usr/bin/env python
#
# Raspberry Pi Control system for home automation.

__author__ = "Caleb Madrigal"
__version__ = "0.0.2"

import zmq
import RPi.GPIO as GPIO
import settings
from flask import Flask, request
from flask.ext.restful import Resource, Api
from time import sleep

############################################################################ Interaction with master

def send_recv_message(message):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:" + str(settings.web_controller_port))
    socket.send(message)
    return socket.recv()

def get_switch(switch_id):
    return send_recv_message("get:"+switch_id)

def set_switch(switch_id, switch_value):
    send_recv_message("set:" + switch_id + "=" + switch_value)

def get_all_switches():
    return send_recv_message("get:all")

def set_all_switches(switch_value):
    send_recv_message("set:all=" + switch_value)

############################################################################################ Classes

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

# Setup RESTful API
app = Flask(__name__)
api = Api(app)
api.add_resource(AllController, '/all/<string:switch_value>')
api.add_resource(SwitchList, '/switch/list')
api.add_resource(SwitchController, '/switch/<string:switch_num>')

@app.route('/')
def main_page():
    with open(settings.index_page_file, "r") as page:
        return page.read()

if __name__ == '__main__':
    # Run web app and web api
    print "Running web server"
    app.run(host='0.0.0.0', port=80, debug=True)

