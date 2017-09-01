# iDogstra

## Beschreibung

iDogstra ist ein Roboterhund, der dem Nutzer folgen kann. Dabei werden primär
zwei Sensoren verwendet: Bluetooth und Kamera. Bluetooth wird zur Bestimmung
des Abstands des Herrchens zum Roboter verwendet. Die Kamera ermöglicht die
Ausrichtung des Roboters, wobei nach einer konfigurierten Farbe gesucht wird.
Des Weiteren gibt es Infrarot und Ultraschall Sensoren, mit denen einerseits
Kollisionen verhindert werden, und andererseits der Roboter aufgeweckt werden
kann, wenn Veränderungen dieser Sensorwerte festgestellt werden.

## Einrichtung

Benötigt wird ein Lego Mindstorms Roboter, der mit einem Raspberry PI und einem
BrickPi gesteuert wird. Des Weiteren wird mindestens ein Bluetooth Dongle
benötigt (empfohlen sind 2 oder mehr), sowie eine Pi-Kamera die nach vorne
ausgerichtet ist. Ferner werden sowohl ein nach vorne ausgerichteter Infrarot
Sensor, als auch ein nach hinten ausgerichteter Ultraschall Sensor benötigt.
Für die Darstellung der Gesten wird ein Bildschirm benötigt, sowie ein kleiner
Lautsprecher, um Töne abspielen zu können.

Auf dem Pi wird folgende Software benötigt:

* Python3
* OpenCV
* BrickPi Bibliotheken
* Bluetooth/Bluez
* NumPy
* SciPy
* Getch
* tkinter
* picamera

Um Den Roboter starten zu können, ist es sinnvoll dieses Repository in das
Home Verzeichnis des Nutzers pi zu clonen. Anschließend startet man das
Programm mit folgenden Befehlen:

    cd iDogstra/code  # In das Root Verzeichnis des Codes wechseln
    python3 main.py default  # Die Standardlogik des Roboters starten

## Problembehandlung

### Bluetooth "Operation not permitted"

Um die Bluetooth Dongles ansprechen zu können (bzw. genauer: Um den Scan
nach Bluetooth Low Energy Beacons zu aktivieren) werden Root Rechte benötigt.
Da das Ausführen als Root einige Probleme mit sich bringt, kann man folgenden
Workaround nutzen, um das Programm als Nutzer pi auszuführen:

    sudo setcap cap_net_raw,cap_net_admin+eip /srv/hass/hass_venv/bin/python3

Siehe [Referenz](https://github.com/home-assistant/home-assistant/issues/3897)

### Kamera lässt sich nicht öffnen

Die Kamera kann immer nur von einem Programm gleichzeitig angesprochen werden.
Es sollten also alle anderen Programme, die gerade die Kamera in Anspruch
nehmen vorher beendet werden. Zur Not tut es auch ein Neustart des Pis.
