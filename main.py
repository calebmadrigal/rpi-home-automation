import sys
import multiprocessing
import master_controller
import web_controller

if len(sys.argv) > 1 and sys.argv[1] == 'mock':
    import mock_gpio_helper as gpio_helper
else:
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
