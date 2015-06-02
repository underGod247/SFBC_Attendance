from Tkinter import *
from datetime import datetime
import tkMessageBox
import sys
import serial
import dataset

#Initialize serial port here
reader = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0)
db = dataset.connect('sqlite:////home/pi/RFIDattend/RFIDattend.db')
rules = db['rules']

#Define subroutines here 

#the quit function - clean up and get out
def getout(*args):
    if tkMessageBox.askyesno("Quit", "Are you sure?"):
        root.destroy()

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)

def update_fields(event=None):
    global late_hr
    global late_min
    global mem_dev
    temp = rules.find_one(name='rule0')
    if not temp:
        tkMessageBox.showinfo("Oops", "No configured rule.")
        late_hr.set('')
        late_min.set('')
        mem_dev.set('')
    else:
        late_hr.set(temp['late_hour'])
        late_min.set(temp['late_minute'])
        mem_dev.set(temp['mem_device'])
    return "break"

def save_changes():
    global late_hr
    global late_min
    global mem_dev
    if tkMessageBox.askyesno("Save?", "Save changes to values?"):
        rule = dict(name='rule0', late_hour=late_hr.get(), late_minute=late_min.get(), mem_device=mem_dev.get())
        rules.upsert(rule, ['name'])
        tkMessageBox.showinfo("Success!", "Changes saved.")
    return "break"

def run_report(event=None):
    report_result = rules.all()
    report_name = datetime.now().strftime("Report_%m%d%y_%H%M%S.csv")
    dataset.freeze(report_result, format='csv', filename=report_name)
    tkMessageBox.showinfo("Succes", "Report saved!")
    return "break"

#set up the main window here
root = Tk()
root.attributes("-fullscreen", True)
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)

#Define variables here
fullscreen = True
late_hr = StringVar()
late_min = StringVar()
mem_dev = StringVar()
email = StringVar()

#Define widgits here 
Label(mainframe, text="Late Hr (0-23):", font = ('TkDefaultFont', 14)).grid(row = 1, column = 1, columnspan = 2, sticky = W)
Entry(mainframe, textvariable = late_hr, font = ('TkDefaultFont', 14), width = 2).grid(row = 1, column =3, sticky = (E, W))
Label(mainframe, text="Late Min(0-59):", font = ('TkDefaultFont', 14)).grid(row = 2, column = 1, columnspan = 2, sticky = W)
Entry(mainframe, textvariable = late_min, font = ('TkDefaultFont', 14), width = 2).grid(row = 2, column = 3, sticky = (E, W))
Label(mainframe, text="Dev:  ", font = ('TkDefaultFont', 14)).grid(row = 3, column = 1, sticky = W)
Entry(mainframe, textvariable = mem_dev, font = ('TkDefaultFont', 14), width = 21).grid(row = 3, column = 2, columnspan = 3, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 6)).grid(row = 6, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text='Reset', command = update_fields).grid(row=7, column = 1, columnspan = 4, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 1)).grid(row = 8, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text='Save', command = save_changes).grid(row=9, column = 1, columnspan = 4, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 32)).grid(row = 10, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text='QUIT', command = getout).grid(row=11, column = 1, columnspan = 4, sticky = (E, W))

#Take care of bindings here
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', getout)


update_fields()
root.mainloop()

