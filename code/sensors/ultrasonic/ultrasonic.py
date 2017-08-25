#Bibliotheken einbinden
import RPi.GPIO as GPIO
import time

class UltraSonic:
    def __init__(self):
        self.MAX_VALUE = 300
    
    def init(self):
        #GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)
    
        #GPIO Pins zuweisen
        GPIO_TRIGGER = 26
        GPIO_ECHO = 20
    
        #Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(GPIO_ECHO, GPIO.IN)
 
    def get_Distanz(self):
        # setze Trigger auf HIGH
        GPIO.output(GPIO_TRIGGER, True)
    
        # setze Trigger nach 0.01ms aus LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)
 
        StartZeit = time.time()
        StopZeit = time.time()
 
        # speichere Startzeit
        while GPIO.input(GPIO_ECHO) == 0:
            StartZeit = time.time()
 
        # speichere Ankunftszeit
        while GPIO.input(GPIO_ECHO) == 1:
            StopZeit = time.time()
 
        # Zeit Differenz zwischen Start und Ankunft
        TimeElapsed = StopZeit - StartZeit
        # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
        # und durch 2 teilen, da hin und zurueck
        distanz = (TimeElapsed * 34300) / 2
 
        return distanz
 
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