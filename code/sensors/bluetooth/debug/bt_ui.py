import tkinter as tk
from tkinter import ttk
from threading import Thread

EXPAND = tk.W + tk.E + tk.S + tk.N


class BTValueDebugger(ttk.Frame):
    def __init__(self, master: tk.Tk = None):

        ttk.Frame.__init__(self, master if master is not None else tk.Tk())

        self.root = self.master
        self.root.protocol("WM_DELETE_WINDOW", self.exit)
        self.root.attributes('-fullscreen', True)
        self.root.title('Debugging')

        self.__frames = None

        self.__setup_window()
        self.__create_widgets()

        self.__delta_max = 1
        self.__delta_min = -1
        self.__last_value = (None, None)

    def __setup_window(self):
        self.grid(sticky=EXPAND, padx=10, pady=5)
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

    def __create_widgets(self):
        self.fr_main = ttk.Frame(self)
        self.fr_main.pack(fill=tk.BOTH, expand=True)

        self.lbl_values = ttk.Label(self.fr_main)
        self.lbl_values.pack(fill=tk.BOTH, expand=True)

    def exit(self) -> None:
        self.master.destroy()
        self.quit()

    def start(self):
        self.root.after(0, self.update_ui)
        Thread(target=self.mainloop()).start()

    def __start(self):
        self.mainloop()

    def update_values(self, new_value):
        delta = new_value[0] - new_value[1]

        self.__delta_max = max(self.__delta_max, delta)
        self.__delta_min = min(self.__delta_min, delta)

        self.__last_value = new_value

    def update_ui(self):
        self.lbl_values['text'] = self.__last_value

if __name__ == '__main__':
    deb = BTValueDebugger()
    deb.start()

    import random
    while True:
        deb.update_values((random.randint(0, 255), random.randint(0, 255)))

