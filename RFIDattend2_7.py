from Tkinter import *
from datetime import datetime
import tkMessageBox
import sys
import serial
import dataset
import time

#Initialize serial port here
reader = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0)
db = dataset.connect('sqlite:////home/pi/RFIDattend/RFIDattend.db')
members = db['members']
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

def search_id():
    global members
    global rfid_val
    global name
    global this_attendance_count
    global this_late_count
    if len(rfid_val.get()) != 12:
        show_red_iderror()
        return False 
    else:
        temp = members.find_one(rfid=rfid_val.get())
    if not temp:
        show_red_notfound()
        name.set('')
        return False
    else:
        name.set(temp['name'])
    if temp['checked_in']:
        show_yellow()
        return False
    else:
        this_attendance_count = temp['attendance_count']
        this_late_count = temp['late_count']
    return True

def save_changes():
    global members
    global rfid_val
    global this_attendance_count
    global this_late_count
    this_date = datetime.now().strftime("%m/%d/%y")
    this_time = datetime.now().strftime("%H:%M:%S")
    if is_late():
        this_attendance_count += 1
        this_late_count += 1
        show_green()
    else:
        this_attendance_count += 1
        show_green()
    member = dict(rfid=rfid_val.get(), last_date=this_date, last_time=this_time, attendance_count=this_attendance_count, late_count=this_late_count, checked_in=1)
    members.update(member, ['rfid'])
    return "break"

def is_late():
    global late_hr
    global late_min
    rightnow = datetime.now()
    islate = False
    try:
        latetime = rightnow.replace(hour = late_hr, minute = late_min, second = 0, microsecond = 0)
    except:
        islate = False

    if rightnow <= latetime:
        islate = False

    elif rightnow > latetime:
        islate = True

    return islate

def reset_fields():
    global rfid_val
    global name
    rfid_val.set('No ID')
    name.set('')
    return "break"

def set_rules():
    global late_hr
    global late_min
    global mem_dev

    temp = rules.find_one(name='rule0')
    if not temp:
        return "break"
    else:
        try:
            late_hr = int(temp['late_hour'])
        except:
            pass
        try:
            late_min = int(temp['late_minute'])
        except:
            pass
        mem_dev = temp['mem_device']
    return "break"


def receivedID(event=None):
    global reader
    global rfid_val
    if reader.inWaiting() > 0:
        _receivedID=reader.readline()[1:13]
        rfid_val.set(_receivedID)
        if search_id():
            save_changes()
        root.after(2250, show_blank)
        root.after(2250, receivedID)
        reader.flushInput()
        reader.flushOutput()
    else:
        root.after(500, receivedID)
    return "break"

def show_red_iderror():
    global red
    global status
    status_label.configure(image = red)
    status.set("ID read error - please try again.")
    return "break"

def show_red_notfound():
    global red
    global status
    status_label.configure(image = red)
    status.set("ID not found - please try again.")
    return "break"

def show_green():
    global green
    global status
    status_label.configure(image = green)
    status.set("Welcome! Attendance recorded.")
    return "break"

def show_yellow():
    global yellow
    global status
    status_label.configure(image = yellow)
    status.set("Check-in already recorded.")
    return "break"

def show_blank():
    global blank
    global status
    reset_fields()
    status_label.configure(image = blank)
    status.set("Ready...")
    return "break"

def set_clock():
    global date_now
    global time_now
    date_now.set(datetime.now().strftime("%m/%d/%y"))
    time_now.set(datetime.now().strftime("%H:%M:%S"))
    root.after(329, set_clock)



#set up the main window here
root = Tk()
root.attributes("-fullscreen", True)
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)

#Define variables here
fullscreen = True
name = StringVar()
rfid_val = StringVar()
date_now = StringVar()
time_now = StringVar()
status = StringVar()
status.set("Initializing...")
rfid_val.set('Please wait...')
green = PhotoImage(file = "assets/green_icon.gif")
yellow = PhotoImage(file = "assets/yellow_icon.gif")
red = PhotoImage(file = "assets/red_icon.gif")
blank = PhotoImage(file = "assets/empty_icon.gif")
this_attendance_count = 0
this_late_count = 0
late_hr = 0
late_min = 0
mem_dev = "/dev/null"

#Define widgits here

Label(mainframe, textvariable = date_now, font = ('TkDefaultFont', 14)).grid(row = 1, column = 1, columnspan = 2, sticky = (E, W))
Label(mainframe, textvariable = time_now, font = ('TkDefaultFont', 14)).grid(row = 1, column = 3, columnspan = 2, sticky = (E, W))
Label(mainframe, text="ID: ", font = ('TkDefaultFont', 14)).grid(row = 2, column = 1, sticky = W)
Entry(mainframe, textvariable = rfid_val, font = ('TkDefaultFont', 14)).grid(row = 2, column =2, columnspan = 3, sticky = (E, W))
Label(mainframe, text="Name:  ", font = ('TkDefaultFont', 14)).grid(row = 3, column = 1, sticky = W)
name_entry = Entry(mainframe, textvariable = name, font = ('TkDefaultFont', 14))
name_entry.grid(row = 3, column = 2, columnspan = 3, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 12)).grid(row = 4, column = 1, columnspan = 4, sticky = (E, W))
status_label = Label(mainframe, image=yellow)
status_label.grid(row = 5, column = 1, columnspan = 4, sticky = (E, W))
Label(mainframe, textvariable = status, font = ('TkDefaultFont', 14)).grid(row = 6, column = 1, columnspan = 4, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 16)).grid(row = 7, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text='QUIT', command = getout).grid(row=8, column = 1, columnspan = 4, sticky = (E, W))

#Take care of bindings here
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', getout)

reader.flushInput()
reader.flushOutput()
set_rules()
root.after(1000, show_blank)
root.after(500, receivedID)
root.after(329, set_clock)
root.mainloop()
