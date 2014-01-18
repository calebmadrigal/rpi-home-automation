# Raspberry Pi Home Security System - settings

__author__ = "Caleb Madrigal"

# Web interface settings
hostname = "0.0.0.0"
port = 80
#port = 8007

#state_file = "state.json"
state_file = "/home/pi/rpi-home-automation/state.json"

credentials_file = "/home/pi/rpi-home-automation/credentials.json"

# Index page
#index_page_file = "index.html"
index_page_file = "/home/pi/rpi-home-automation/index.html"

# Switch data
switches = ['1', '2', '3']
on_pins = [9, 1, 7]
off_pins = [11, 0, 8]
switch_pulse_time_in_secs = 1.5

# Door sensor data
door_sensor_pin = 24
door_sensor_bounce_time = 36 * 60 * 1000 # 36 min

# Alarm stuff
alarm_duration = 30 #seconds

# 0MQ Connection stuff
web_controller_conn_str = "tcp://127.0.0.1:30000"
switch_worker_conn_str = "tcp://127.0.0.1:30001"

# Logging files
#web_log_file = "homesec_web.log"
web_log_file = "/var/log/homesec_web.log"

#master_log_file = "homesec_master.log"
master_log_file = "/var/log/homesec_master.log"

#gpio_log_file = "homesec_gpio.log"
gpio_log_file = "/var/log/homesec_gpio.log"

