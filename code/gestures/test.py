# basic code from >>
# http://tkinter.unpythonic.net/wiki/PhotoImage

# extra code -------------------------------------------------------------------------
from __future__ import print_function

try:
    import tkinter as tk
except:
    import Tkinter as tk

import sys
import platform

print ()
print ('python    ', sys.version)
print ('tkinter   ', tk.TkVersion)
print ()
print (platform.platform(),' ',platform.machine())
print ()


# basic code -------------------------------------------------------------------------

root = tk.Tk()

def create_button_with_scoped_image():
    # "w6.gif" >>
    # http://www.inf-schule.de/content/software/gui/entwicklung_tkinter/bilder/w6.gif
    img = tk.PhotoImage(file="neutral.gif")  # reference PhotoImage in local variable
    button = tk.Button(root, image=img)
    # button.img = img  # store a reference to the image as an attribute of the widget
    button.image = img  # store a reference to the image as an attribute of the widget
    button.grid()

create_button_with_scoped_image()

tk.mainloop()