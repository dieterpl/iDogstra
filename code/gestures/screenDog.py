from Tkinter import *
import time

class ScreenDog:
    def __init__(self):
        self.DEFAULT="test"

    def changeKeyEvent(self):
        return 0

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

if __name__ == '__main__':
    try:
        root=Tk()
        app=FullScreenApp(root)
        imgPath = r"neutral.gif"
        photo = PhotoImage(file = imgPath)
        label = Label(image = photo)
        label.image = photo # keep a reference!
        label.grid(row = 3, column = 1, padx = 5, pady = 5)
        root.mainloop()
        # Beim Abbruch durch STRG+C resetten
    except KeyboardInterrupt:
        print("Messung vom User gestoppt")
    
    

