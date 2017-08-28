import tkinter as tk
import time
from threading import Thread

class Gesture():
    neutral = r"neutral.gif"
    confused = r"confused.gif"

class ScreenDog:
    def __init__(self):
        self.DEFAULT = Gesture.confused
        self.current_state = self.DEFAULT
        self.window = None
        self.root = None

    def open_window(self):
        self.root = tk.Tk()
        # set the dimensions of the screen
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (800, 480, 0, 0))
        self.root.attributes('-alpha', 0.0) #For icon
        self.root.lower()
        self.root.iconify()
        self.window = tk.Toplevel(self.root)
        self.window.geometry("800x480") #Whatever size
        self.window.overrideredirect(1) #Remove border
        self.window.attributes('-topmost', 1)
        #Whatever buttons, etc

        print(Gesture.confused)
        self.imgPath = Gesture.confused
        self.photo = tk.PhotoImage(file = self.imgPath)
        self.label = tk.Label(self.window,image = self.photo)
        self.label.image = self.photo # keep a reference!
        self.label.grid(row = 3, column = 1, padx = 5, pady = 5)
        self.label.pack(fill = tk.BOTH, expand = 1)
        self.root.after(10, self.task)
        self.window.mainloop()

    def start(self):
        self.t = Thread(target=self.open_window)
        self.t.start()


    def task(self):
        #print("hello")
        self.root.after(1, self.task)  # reschedule event in 2 seconds


    def changeState(self, gesture):
        self.imgPath = gesture
        self.photo = tk.PhotoImage(file=self.imgPath)
        self.label.image = self.photo
        return 0


if __name__ == '__main__':
    try:

        sd = ScreenDog()
        sd.start()
        print ("test1")
        time.sleep(0.5)
        sd.changeState(Gesture.neutral)
        print ("test")




        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
    
    

