import Tkinter as tk
import time
from enum import Enum

class Gesture(Enum):
    neutral = r"neutral.gif"
    confused = r"confused.gif"


class ScreenDog:
    def __init__(self):
        self.DEFAULT=Gesture.neutral
        self.current_state = self.DEFAULT
        self.root = tk.Tk()
        # set the dimensions of the screen
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (800, 480, 0, 0))
        self.root.attributes('-alpha', 0.0) #For icon
        self.root.lower()
        self.root.iconify()
        self.window = tk.Toplevel(root)
        self.window.geometry("800x480") #Whatever size
        self.window.overrideredirect(1) #Remove border
        self.window.attributes('-topmost', 1)
        #Whatever buttons, etc


        self.imgPath = self.current_state
        self.photo = tk.PhotoImage(file = imgPath)
        self.label = tk.Label(window,image = photo)
        self.label.image = photo # keep a reference!
        self.label.grid(row = 3, column = 1, padx = 5, pady = 5)
        self.label.pack(fill = tk.BOTH, expand = 1)
        self.window.mainloop()

    def changeState(self, gesture):

        return 0


if __name__ == '__main__':
    try:
        sd = ScreenDog()
        sd.changeState(Gesture.confused)
        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
    
    

