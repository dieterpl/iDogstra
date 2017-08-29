import serial
import sys
import time

Zeichen = 0
Laenge = 0
Qualitaet = 0
Satelliten = 0

Hoehe = 0.0
Breitengrad = 0.0
Laengengrad = 0.0

Input = ""
Uhrzeit = ""
Checksumme = ""

Datenliste = []

# open UART
UART = serial.Serial("/dev/ttyUSB0", 4800)

while True:

    Zeichen = 0

    Input = ""

    # get char
    Zeichen = UART.read()

    # test if transmission has started
    if Zeichen == "$":

        # read char 2-6
        for Counter in range(4):

            Zeichen = 0
            Zeichen = UART.read()
            Input = Input + str(Zeichen)

		# test whether sending protocoll matches GPGG
        if Input == "GPGG":

            # read chars until LF
            while Zeichen != "\n":
                Zeichen = 0
                Zeichen = UART.read()
                Input = Input + str(Zeichen)

            Input = Input.replace("\r\n", "")

            # split after every "," and save to list
            Datenliste = Input.split(",")

            # get length of data
            Laenge_Daten = len(Input)

            # get timestamps
            Uhrzeit = Datenliste[1]
            Uhrzeit = Uhrzeit[0:2] + ":" + Uhrzeit[2:4] + ":" + Uhrzeit[4:6]

            # get longitude and latitude values
            Breitengrad = int(float(Datenliste[2]) / 100)
            Laengengrad = int(float(Datenliste[4]) / 100)

            Breitenminute = float(Datenliste[2]) - (Breitengrad * 100)
            Laengenminute = float(Datenliste[4]) - (Laengengrad * 100)

            Breite = round(Breitengrad + (Breitenminute / 60), 6)
            Laenge = round(Laengengrad + (Laengenminute / 60), 6)

            # get signal strength
            Qualitaet = int(Datenliste[6])

            # get number of satellites
            Satelliten = int(Datenliste[7])

            # get altitude
            Hoehe = float(Datenliste[9])

            # get checksum
            Checksumme = Datenliste[14]

            # debug print out
            print(Input)
            print("")
            print("Laenge des Datensatzes:", Laenge_Daten, "Zeichen")
            print("Uhrzeit:", Uhrzeit)
            print("Breitengrad:", Breite, "Grad", Datenliste[3])
            print("Laengengrad:", Laenge, "Grad", Datenliste[5])
            print("Hoehe ueber dem Meeresspiegel:", Hoehe, Datenliste[10])
            print("GPS-Qualitaet:", Qualitaet)
            print("Anzahl der Satelliten:", Satelliten)
            print("Checksumme:", Checksumme)
            print("-------------------------------------------")
