
# Format of file: 1=on\n2=off\n3=off (meaning switch 1 on, switch 2 and 3 off)
state_file = "state.json"
#state_file = "/home/pi/rpi-home-automation/state.json"
#switch_values_file = "/home/pi/rpi-home-automation/switch_values.dat"

# Index page
index_page_file = "index.html"
#index_page_file = "/home/pi/rpi-home-automation/index.html"

# Switch data
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
web_controller_conn_str = "tcp://127.0.0.1:30000"
sensor_watcher_conn_str = "tcp://127.0.0.1:30001"
switch_worker_conn_str = "tcp://127.0.0.1:30002"
