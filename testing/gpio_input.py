import RPi.GPIO as GPIO
from time import sleep

#pins = [0, 1, 4, 17, 21, 22, 10, 9, 11, 18, 23, 24, 25, 8, 7]
INPUT_PIN = 2

GPIO.setmode(GPIO.BCM)
#GPIO.setup(INPUT_PIN, GPIO.IN)
GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 0

def input_callback(channel):
    print "HIT", counter
    counter += 1

GPIO.add_event_detect(INPUT_PIN, GPIO.RISING, callback=input_callback, bouncetime=200)

raw_input("Hit ENTER to exit")
