import tkinter as tk
import time
from threading import Thread


class Screen:

    def __init__(self):
        """
        init the class and shows the window default image configurable
        """
        self.imgPath = "./pics/default.gif"
        self.window = None
        self.root = None
        self.__show_window()

    def __init_root(self):
        self.root = tk.Tk()
        # set the dimensions of the screen
        # and where it is placed
        self.root.geometry('%dx%d+%d+%d' % (800, 480, 0, 0))
        self.root.attributes('-alpha', 0.0)  # For icon
        self.root.lower()
        self.root.iconify()

    def __init_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.geometry("800x480")  # Whatever size
        self.window.overrideredirect(1)  # Remove border
        self.window.attributes('-topmost', 1)

    def __open_window(self):
        """
        privat method to dispaly window on pi in fullscreen
        :return: -
        """
        self.__init_root()
        self.__init_window()
        # Whatever buttons, etc

        self.photo = tk.PhotoImage(file=self.imgPath)
        self.label = tk.Label(self.window, image=self.photo)
        self.label.image = self.photo  # keep a reference!
        self.label.grid(row=3, column=1, padx=5, pady=5)
        self.label.pack(fill=tk.BOTH, expand=1)
        self.root.after(100, self.__change_picture_callback)
        self.window.mainloop()

    def __change_picture_callback(self):
        """
        callback used to update the picture tk interal stuff
        :return:
        """
        self.photo = tk.PhotoImage(file=self.imgPath)
        self.label.configure(image=self.photo)
        self.image = self.photo

        # reschedule event in 2 seconds
        self.root.after(100, self.__change_picture_callback)

    def __show_window(self):
        """
        starts windows in different thread and waits for init
        :return:
        """
        self.t = Thread(target=self.__open_window)
        self.t.start()
        # time to start thread
        time.sleep(2)

    def change_gesture(self, gesture_path):
        """
        method th change the picture by selecting gesture
        :param gesture: string to new image
        :return: -
        """
        self.imgPath = gesture_path


# if __name__ == '__main__':
#    try:
#        sd = ScreenDog()
#        while True:
#            time.sleep(2.5)
#            sd.change_gesture(sd.Gesture.neutral)
#            time.sleep(5.5)
#            sd.change_gesture(sd.Gesture.confused)
#            # Beim Abbruch durch STRG+C resetten
#    except KeyboardInterrupt:
#        print("Messung vom User gestoppt")
