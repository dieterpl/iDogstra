import Tkinter as tk
import time
from enum import Enum
import threading
class Gesture(Enum):
    neutral = r"neutral.gif"
    confused = r"confused.gif"

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class ScreenDog:
    def __init__(self):
        self.DEFAULT = Gesture.confused
        self.current_state = self.DEFAULT

    @threaded
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


        self.imgPath = self.current_state
        self.photo = tk.PhotoImage(file = self.imgPath)
        self.label = tk.Label(self.window,image = self.photo)
        self.label.image = self.photo # keep a reference!
        self.label.grid(row = 3, column = 1, padx = 5, pady = 5)
        self.label.pack(fill = tk.BOTH, expand = 1)
        self.window.mainloop()

    def changeState(self, gesture):
        self.imgPath =gesture


        self.label.update()
        self.window.update()
        self.root.update()
        return 0


if __name__ == '__main__':
    try:

        sd = ScreenDog()
        handle = sd.open_window()
        print handle


        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
    
    

