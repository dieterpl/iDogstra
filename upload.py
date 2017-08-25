#!/usr/bin/python3

import subprocess
import sys

mode = input("WLAN (w) or LAN (l)? ")
ip = ""

if mode == "w":
    ip = "172.28.0.20"
elif mode == "l":
    ip = "192.168.168.255"
else:
    print("Please enter valid mode character")
    sys.exit(1)

subprocess.Popen("rsync -Pra Code/ pi@%s:/home/pi/Code" % ip, shell=True).wait()
