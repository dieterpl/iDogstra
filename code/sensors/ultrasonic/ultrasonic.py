# Bibliotheken einbinden
import time
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print("WARNING: Could not import module RaspberryPI (not running on a raspberry pi?). S module will not "
          "be available.")
    GPIO = None


class UltraSonic:
    def __enter__(self):
        """
        sets GPIO ports and max distance value also setting up pi for us sensor
        :return:
        """
        self.MAX_VALUE = 300
        self.GPIO_TRIGGER = 26
        self.GPIO_ECHO = 20
        # GPIO Modus (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # Richtung der GPIO-Pins festlegen (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)
        return self

    def get_distance(self):
        """
        returns the distance in cm max value means object ist too far or too close
        :return:
        """
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
        distance = (TimeElapsed * 34300) / 2
        if distance > self.MAX_VALUE:
            return self.MAX_VALUE
        return distance

    def __exit__(self, exc_type, exc_value, traceback):
        GPIO.cleanup()


#if __name__ == '__main__':
#    with UltraSonic() as us:
#        print ("Gemessene Entfernung = %.1f cm" % us.get_distance())
