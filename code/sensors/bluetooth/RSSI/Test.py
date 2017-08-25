import Queue
from Bluetooth import Lescan_Thread, Btmon_Thread
from Tkinter import *



hci0_result =Queue.Queue()
hci0_btmon = Btmon_Thread.BtmonThread(result_q=hci0_result, adapter="hci0")


hci1_result =Queue.Queue()
hci1_btmon = Btmon_Thread.BtmonThread(result_q=hci1_result, adapter="hci1")

hci0_lescan=Lescan_Thread.LescanThread("hci0", True)
hci1_lescan=Lescan_Thread.LescanThread("hci1", True)
try:
    hci0_btmon.start()
    hci1_btmon.start()
    hci0_lescan.start()
    hci1_lescan.start()
    
except (KeyboardInterrupt, SystemExit):
    print ('\n! Received keyboard interrupt, quitting threads.\n')
    hci0_btmon.join(100)
    hci1_btmon.join(100)
    hci0_lescan.join(100)
    hci1_lescan.join(100)
    print('Threads stopped')
    

print('Adapters listening')

master = Tk()
master.geometry("370x500+30+30") 
w0 = Scale(master, from_=20, to=90)
w0.pack(fill=BOTH, padx=5, side=LEFT)
w1 = Scale(master, from_=20, to=90)
w1.pack(fill=BOTH, padx=5, side=LEFT)

while True:
    

    if not hci0_result.empty():
        i = hci0_result.get(block=True, timeout=10)
        i = (i+w0.get())/2
        w0.set(i)
        print ('hci0_'+ str(i))
        
        
    if not hci1_result.empty():
        i = hci1_result.get(block=True, timeout=10)
        i = (i+w1.get())/2
        w1.set(i)
        print ('hci1_'+str(i))
    
    master.update_idletasks()
    master.update()
    
    
