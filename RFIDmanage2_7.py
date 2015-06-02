from Tkinter import *
from datetime import datetime
import tkMessageBox
import sys
import serial
import dataset
import os
import shutil

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

def search_name(event=None):
    global members
    global rfid_val
    global name
    global email
    temp = members.find_one(name=name.get())
    if not temp:
        tkMessageBox.showinfo("Oops", "Cannot find that name.")
        rfid_val.set('No ID')
        email.set('')
    else:
        rfid_val.set(temp['rfid'])
        email.set(temp['email'])
    return "break"

def search_id():
    global members
    global rfid_val
    global name
    global email
    if len(rfid_val.get()) != 12:
        tkMessageBox.showerror("Error", "Invalid ID value.")
        reset_fields()
        return "break"
    else:
        temp = members.find_one(rfid=rfid_val.get())
    if not temp:
        tkMessageBox.showinfo("Oops", "Cannot find that ID.")
        name.set('')
        email.set('')
    else:
        name.set(temp['name'])
        email.set(temp['email'])
    return "break"

def delete_member():
    global members
    global rfid_val
    global name
    if len(rfid_val.get()) != 12:
        tkMessageBox.showerror("Error", "Invalid ID value.")
        reset_fields()
        return "break"
    if not len(name.get()):
        tkMessageBox.showerror("Error", "Empty name field.")
        reset_fields()
        return "break"
    if tkMessageBox.askyesno("Delete?", "Delete this member?"):
        members.delete(rfid=rfid_val.get())
    reset_fields()
    return "break"

def save_changes():
    global members
    global rfid_val
    global name
    global email
    if len(rfid_val.get()) != 12:
        tkMessageBox.showerror("Error", "Invalid ID value.")
        reset_fields()
        return "break"
    if not len(name.get()) or (name.get().find(',') != -1):
        tkMessageBox.showerror("Error", "Empty or invalid name field.")
        reset_fields()
        return "break"
    if not len(email.get()) or (email.get().find(',') != -1):
        tkMessageBox.showerror("Error", "Empty or invalid email field.")
        reset_fields()
        return "break"
    if tkMessageBox.askyesno("Save?", "Save changes to values?"):
        member = dict(name=name.get(), rfid=rfid_val.get(), email=email.get())
        members.upsert(member, ['rfid'])
    reset_fields()
    return "break"

def run_report():
    global mem_dev
    report_result = members.all()
    report_name = datetime.now().strftime("Report_%m%d%y_%H%M%S.csv")
    dataset.freeze(report_result, format='csv', filename=report_name)
    #shell_command = "mv " + report_name + " " + mem_dev
    #print shell_command
    try:
        #os.system(shell_command)
        shutil.move(report_name, mem_dev)
    except:
        tkMessageBox.showwarning("Warning!", "Report not moved to USB.")
    else:
        tkMessageBox.showinfo("Succes", "Report saved!")
    return "break"

def new_rehearsal():
    #build the list of IDs from the DB you can't modify entries while iterating through the DB
    if tkMessageBox.askyesno("Continue?", "Start new rehearsal event?"):
        ids = []
        for member in members:
            ids.append(member['rfid'])

        for id_number in ids:
            member = dict(rfid=id_number, checked_in=0)
            members.update(member, ['rfid'])

        model_member = members.find_one(rfid='000000000000')
        model_attendance = model_member['attendance_count']
        model_attendance += 1
        member = dict(rfid='000000000000', attendance_count=model_attendance)
        members.update(member, ['rfid'])

    return "break"

def new_concert():
    if tkMessageBox.askyesno("Continue?", "Start new concert (will zero attendance)?"):
        current_date = datetime.now().strftime("%m/%d/%y")
        current_time = datetime.now().strftime("%H:%M:%S")
        #build the list of IDs from the DB you can't modify entries while iterating through the DB
        ids = []
        for member in members:
            ids.append(member['rfid'])
    
        for id_number in ids:
            member = dict(rfid=id_number, last_date=current_date, last_time=current_time, attendance_count=0, late_count=0)
            members.update(member, ['rfid'])

    return "break"

def reset_fields():
    global rfid_val
    global name
    global email
    rfid_val.set('No ID')
    name.set('')
    email.set('')
    return "break"

def set_rules():
    global mem_dev
    temp = rules.find_one(name='rule0')
    mem_dev = temp['mem_device']
    return "break"

def receivedID(event=None):
    global reader
    global rfid_val
    if reader.inWaiting() > 0:
        _receivedID=reader.readline()[1:13]
        rfid_val.set(_receivedID)
        reader.flushInput()
        reader.flushOutput()
    root.after(500, receivedID)
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
name = StringVar()
rfid_val = StringVar()
rfid_val.set('No ID')
email = StringVar()
mem_dev = ""

#Define widgits here 
Label(mainframe, text="ID:", font = ('TkDefaultFont', 14)).grid(row = 1, column = 1, sticky = W)
Entry(mainframe, textvariable = rfid_val, font = ('TkDefaultFont', 14)).grid(row = 1, column =2, columnspan = 3, sticky = (E, W))
Label(mainframe, text="Name: ", font = ('TkDefaultFont', 14)).grid(row = 2, column = 1, sticky = W)
name_entry = Entry(mainframe, textvariable = name, font = ('TkDefaultFont', 14))
name_entry.grid(row = 2, column = 2, columnspan = 3, sticky = (E, W))
Label(mainframe, text="Email:  ", font = ('TkDefaultFont', 14)).grid(row = 3, column = 1, sticky = W)
Entry(mainframe, textvariable = email, font = ('TkDefaultFont', 14)).grid(row = 3, column = 2, columnspan = 3, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 3)).grid(row = 4, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text="Search Name", command = search_name).grid(row = 5, column = 1, columnspan = 2, sticky = (E, W))
Button(mainframe, text="Search ID", command = search_id).grid(row = 5, column = 3, columnspan = 2, sticky = (E, W))
Button(mainframe, text="Delete Member", command = delete_member).grid(row = 6, column = 1, columnspan = 2, sticky = (E, W))
Button(mainframe, text="Save Changes", command = save_changes).grid(row = 6, column = 3, columnspan = 2, sticky = (E, W))
Button(mainframe, text="Clear Fields", command = reset_fields).grid(row = 7, column = 1, columnspan = 2, sticky = (E, W))
Button(mainframe, text="Run Report", command = run_report).grid(row = 7, column = 3, columnspan = 2, sticky = (E, W))
Button(mainframe, text="New Rehearsal", command = new_rehearsal).grid(row = 8, column = 1, columnspan = 2, sticky = (E, W))
Button(mainframe, text="New Concert", command = new_concert).grid(row = 8, column = 3, columnspan = 2, sticky = (E, W))
Label(mainframe, text=" ", font = ('TkDefaultFont', 3)).grid(row = 9, column = 1, columnspan = 4, sticky = (E, W))
Button(mainframe, text='QUIT', command = getout).grid(row=10, column = 1, columnspan = 4, sticky = (E, W))

#Take care of bindings here
set_rules()
name_entry.focus()
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', getout)
root.bind('<Return>', search_name)

root.after(500, receivedID)
root.mainloop()

