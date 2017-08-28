import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP =  # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

# Configure for an EV3 color sensor.
# BP.set_sensor_type configures the BrickPi3 for a specific sensor.
# BP.PORT_1 specifies that the sensor will be on sensor port 1.
# BP.Sensor_TYPE.EV3_INFRARED_PROXIMITY specifies that the sensor will be an EV3 infrared sensor.


BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.EV3_INFRARED_PROXIMITY)

def scanCollision():
    try:
        print(BP.get_sensor(BP.PORT_1))   # print the infrared value
        if (BP.get_sensor(BP.PORT_1) <= 70):
            print("DANGER DANGER")
            #setPos.headshake()
            
    except brickpi3.SensorError as error:
        print(error)
            

try:
    while True:
        # BP.get_sensor retrieves a sensor value.
        # BP.PORT_1 specifies that we are looking for the value of sensor port 1.
        # BP.get_sensor returns the sensor value (what we want to display).
        try:
            scanCollision()
                
        except brickpi3.SensorError as error:
            print(error)
        
        time.sleep(0.5)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
# Bibliotheken einbinden
import RPi.GPIO as GPIO
import time


class InfraRed:
    def __init__(self):
        self.SENSOR_PORT = BP.PORT_1
        self.BRICKPI = brickpi3.BrickPi3()
        self.GPIO_ECHO = 20
        self.initialized = False

    def init(self):
        # GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

    def get_distance(self):
        if (not self.initialized):
            self.init()
            self.initialized = True
        # setze Trigger auf HIGH
        GPIO.output(self.GPIO_TRIGGER, True)

        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.01)
        GPIO.output(self.GPIO_TRIGGER, False)

        StartZeit = time.time()
        StopZeit = time.time()

        # speichere Startzeit
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartZeit = time.time()

        # speichere Ankunftszeit
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopZeit = time.time()

        # Zeit Differenz zwischen Start und Ankunft
        TimeElapsed = StopZeit - StartZeit
        # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        return (TimeElapsed * 34300) / 2


if __name__ == '__main__':
    try:
        us = UltraSonic()
        while True:
            print ("Gemessene Entfernung = %.1f cm" % us.get_Distanz())
            time.sleep(1)

            # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
        GPIO.cleanup()
