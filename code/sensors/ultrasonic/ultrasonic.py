# Bibliotheken einbinden
import RPi.GPIO as GPIO
import time


class UltraSonic:
    def __init__(self):
        self.MAX_VALUE = 300
        self.GPIO_TRIGGER = 26
        self.GPIO_ECHO = 20
        self.init()

    def __enter__(self):
        # GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

    def get_distance(self):

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

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()



if __name__ == '__main__':
    try:
        with UltraSonic() as us:
            print ("Gemessene Entfernung = %.1f cm" % us.get_distance())
            time.sleep(1)

            # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")

