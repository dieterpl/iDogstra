import os
import tkinter as tk
import time
from threading import Thread
from config import config


class Screen:

    def __init__(self, initial_picture="init.gif"):
        """
        init the class and shows the window default image configurable
        """
        self.imgPath = os.path.join(config.PICTUREPATH, initial_picture)

        self.__init_root()
        self.__init_window()

        self.__show_window()

    def __init_root(self):
        # set the dimensions of the screen
        # and where it is placed
        self.root = tk.Tk()
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

    def change_picture(self, picture_path):
        """
        method th change the picture by selecting gesture
        :param gesture_path: string to new image
        :return: -
        """
        self.imgPath = picture_path
