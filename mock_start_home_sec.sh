#!/bin/bash
echo "Starting master_controller"
python master_controller.py &
echo "Starting switch_worker"
python mock_switch_worker.py &
echo "Starting sensor_watcher"
python mock_sensor_watcher.py &
echo "Starting web_controller"
python web_controller.py &
echo "All started"

