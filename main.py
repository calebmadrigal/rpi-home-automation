#!/usr/bin/env python
#
# Raspberry Pi Home Security System - main

__author__ = "Caleb Madrigal"
__version__ = "0.0.3"

import multiprocessing
import master_controller
import web_controller
import gpio_helper


def main():
    run_funcs = [master_controller.run, web_controller.run, gpio_helper.run]
    processes = []
    for run in run_funcs:
        p = multiprocessing.Process(target=run)
        p.daemon = True
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
