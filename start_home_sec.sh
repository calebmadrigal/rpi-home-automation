#!/bin/bash
echo "Starting master_controller"
python master_controller.py &
echo "Starting switch_worker"
python switch_worker.py &
echo "Starting sensor_watcher"
python sensor_watcher.py &
echo "Starting web_controller"
python web_controller.py &
echo "All started"

