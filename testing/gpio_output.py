import RPi.GPIO as GPIO
from time import sleep

pins = [0, 1, 4, 17, 21, 22, 10, 9, 11, 18, 23, 24, 25, 8, 7]

GPIO.setmode(GPIO.BCM)
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

def pulse_pin(pin):
    print "Pulsing pin", pin
    GPIO.output(pin, True)
    sleep(1.5)
    GPIO.output(pin, False)

