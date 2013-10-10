from flask import Flask, request
from flask.ext.restful import Resource, Api


########################################################################################## Constants

# Storage location
#
# Format: 1=1\n2=0\n3=0 (meaning switch 1 on, switch 2 and 3 off)
switch_values_file = "switch_values.dat"

# Pin definitions
switches = [1, 2, 3]
on_pins = [9, 1, 7]
off_pins = [11, 0, 8]


########################################################################################## Functions
def pulse_pin(pin):
    print "Pulse pin", pin
    #GPIO.output(pin, True)
    sleep(1)
    #GPIO.output(pin, False)

def set_switch(switch_num, value):
    if value == '1':
        pulse_pin(on_pins[int(switch_num)-1])
    elif value == '0':
        pulse_pin(off_pins[int(switch_num)-1])

def read_switch_data():
    with open(switch_values_file, "r") as f:
        lines = f.readlines()
        switch_data_list = [line.split('=') for line in lines]
        switch_data_list_cleaned = [(k.strip(), v.strip()) for (k,v) in switch_data_list]
    return dict(switch_data_list_cleaned)

def write_switch_data(switch_data):
    with open(switch_values_file, "w") as f:
        for (k,v) in switch_data.items():
            f.write(k + '=' + v + '\n')

def set_and_save_switch(switch_num, value):
    switch_data = read_switch_data()
    switch_data[switch_num] = value
    write_switch_data(switch_data)
    set_switch(switch_num, value)

def read_switch_value(switch_num):
    switch_data = read_switch_data()
    return switch_data[switch_num]
    
def all_on():
    write_switch_data({switch_num: '1' for switch_num in switches})
    for switch_num in switches:
        set_switch(switch_num, '1')

def all_off():
    write_switch_data({switch_num: '0' for switch_num in switches})
    for switch_num in switches:
        set_switch(switch_num, '0')

############################################################################################# Classes
class SwitchController(Resource):
    def get(self, switch_num):
        return {switch_num: read_switch_value(switch_num)}

    def put(self, switch_num):
        switch_value = request.form['value']
        set_and_save_switch(switch_num, switch_value)
        return {switch_num: switch_value}

class AllOnController(Resource):
    def put(self):
        all_on()
        return {'message': 'success'}

class AllOffController(Resource):
    def put(self):
        all_off()
        return {'message': 'success'}

############################################################################################### Code
app = Flask(__name__)
api = Api(app)

#GPIO.setmode(GPIO.BCM)

# Set pins to output mode
#for pin in on_pins + off_pins:
#    GPIO.setup(pin, GPIO.OUT)
#    GPIO.output(pin, False)

api.add_resource(SwitchController, '/switch/<string:switch_num>')
api.add_resource(AllOnController, '/allon')
api.add_resource(AllOffController, '/alloff')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9003, debug=True)

