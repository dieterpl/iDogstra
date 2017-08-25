'''
Created on 07.08.2017

@author: spaeth
'''
import os
import signal
import threading
import subprocess
from multiprocessing.forking import Popen


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
class BtmonThread(threading.Thread):
    def __init__(self, result_q, adapter):
        super(BtmonThread, self).__init__()
        self.result_q = result_q
        self.adapter=adapter
        self.p = Popen

        
    def run(self):
        self.p = subprocess.Popen(['btmon', '-i', self.adapter],stdout=subprocess.PIPE, bufsize=1,preexec_fn=os.setsid)

        try:
            for line in iter(self.p.stdout.readline, ""):
                if("RSSI" in line):
                    if(RepresentsInt(line[14:17])):
                        self.result_q.put(int(line[14:17])*-1)
#                         print(self.adapter +":\t"+ str(int(line[14:17])*-1))
                    else:
                        print(self.adapter +":\t"+ line)
        except KeyboardInterrupt:
            self.p.kill()

    def join(self, timeout=None):
#         self.p.kill()
#         self.p.wait()
#         self.p.stdout.close()
        os.killpg(os.getpgid(self.p.pid), signal.SIGTERM)
        super(BtmonThread, self).join(timeout)
