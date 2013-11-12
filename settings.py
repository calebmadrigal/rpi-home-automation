
# Format of file: 1=on\n2=off\n3=off (meaning switch 1 on, switch 2 and 3 off)
switch_values_file = "/home/pi/rpi-home-automation/switch_values.dat"

# Index page
index_page_file = "/home/pi/rpi-home-automation/index.html"

# Switch data
switch_options = ['on', 'off']
switches = ['1', '2', '3']

# Actuator pin data
on_pins = [9, 1, 7]
off_pins = [11, 0, 8]
switch_pulse_time_in_secs = 1.5

# Door sensor data
door_sensor_pin = 24
alarm_time_on = 5 #seconds
door_sensor_bounce_time = 34 * 60 * 1000 # 34 min

# 0MQ Connection stuff
web_controller_port = 30000
switch_worker_port = 30002
