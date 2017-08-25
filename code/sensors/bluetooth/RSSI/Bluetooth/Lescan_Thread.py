'''
Created on 07.08.2017

@author: spaeth
'''
import os
import threading
import subprocess
import signal
from multiprocessing.forking import Popen


class LescanThread(threading.Thread):
    def __init__(self, adapter, whitelist=False):
        super(LescanThread, self).__init__()
        self.adapter=adapter
        self.whitelist=whitelist
        self.p = Popen

        
    def run(self):
        if(self.whitelist):
            self.p = subprocess.Popen(['hcitool', '-i', self.adapter, 'lescan', '--whitelist'],stdout=subprocess.PIPE, bufsize=-1, preexec_fn=os.setsid)
        else:
            self.p = subprocess.Popen(['hcitool', '-i', self.adapter, 'lescan'],stdout=subprocess.PIPE, bufsize=-1, preexec_fn=os.setsid)

        try:
            for line in iter(self.p.stdout.readline, ""):
                print(line)
        except KeyboardInterrupt:
            os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)

    def join(self, timeout=None):
        os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)
        super(LescanThread, self).join(timeout)
