from Tkinter import *
from datetime import datetime
import tkMessageBox
import sys
import serial
import dataset

#Initialize serial port here
reader = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0)
db = dataset.connect('sqlite:////home/pi/RFIDattend/RFIDattend.db')
members = db['members']

print("Attendance DB tool...")
command = raw_input("Delete all members [y/N]: ")
if command == '' or command == 'n' or command == 'N':
    print("Proceeding to edit...")
    print(" ")
elif command == 'y' or command == 'Y':
    command = raw_input("Are you sure [y/N]: ")
    if command == '' or command == 'n' or command == 'N':
        print("That was close. Exiting...")
        exit()
    elif command == 'y' or command == 'Y':
        members.drop()
        print("Deleted all members.  Exiting...")
        members = db['members']
        member = dict(id=1, rfid='000000000000', name='Model Member', email='attendance@sfbc.org', attendance_count=0, late_count=0, checked_in=0, last_date='01/01/90', last_time='23:59:59')
        members.insert(member)
        exit()
    else:
        print("Invalid option.  Exiting...")
        exit()
else:
    print("Invalid option. Exiting...")
    exit()
temp_id = int(raw_input("Look up table ID#: "))
temp = members.find_one(id=temp_id)
if not temp:
    print("Could not find ID.")
    exit()
print("Found record for " + temp['name'])
command = raw_input("Delete this record [y/N]: ")
if command == '' or command == 'n' or command == 'N':
    print("Proceeding to edit...")
elif command == 'y' or command == 'Y':
    members.delete(id=temp_id)
    print("Deleted member... exiting.")
    exit()
else:
    print("Invalid option. Exiting...")
    exit()
print(" ")
print("RFID: " + temp['rfid'])
new_rfid = raw_input("New RFID: ")
if not new_rfid:
    new_rfid = temp['rfid']
    print("No change to rfid.")
print(" ")
print("Name: " + temp['name'])
new_name = raw_input("New name: ")
if not new_name:
    new_name = temp['name']
    print("No change to name.")
print(" ")
print("Email: " + temp['email'])
new_email = raw_input("New email: ")
if not new_email:
    new_email = temp['email']
    print("No change to email.")
print(" ")
print("# Att'd: " + str(temp['attendance_count']))
new_att = raw_input("New # Att'd: ")
if not new_att:
    new_attendance_count = temp['attendance_count']
    print("No change to # Att'd.")
else:
    new_attendance_count = int(new_att)
print(" ")
print("# Late: " + str(temp['late_count']))
new_late = raw_input("New # late: ")
if not new_late:
    new_late_count = temp['late_count']
    print("No change to # Late.")
else:
    new_late_count = int(new_late)
print(" ")
command = raw_input("Reset checked in flag [y/N]: ")
if command == '' or command == 'n' or command == 'N':
    new_checked_in = temp['checked_in']
    print("No change to checked in flag.")
elif command == 'y' or command == 'Y':
    new_checked_in = 0
else:
    new_checked_in = temp['checked_in']
    print("Invalid option.  No change.")
print(" ")
print("Last date: " + temp['last_date'])
new_last_date = raw_input("New last date: ")
if not new_last_date:
    new_last_date = temp['last_date']
    print("No change to last date.")
print(" ")
print("Last time: " + temp['last_time'])
new_last_time = raw_input("New last time: ")
if not new_last_time:
    new_last_time = temp['last_time']
    print("No chaange to last time.")
print(" ")
command = raw_input("Save changes [y/N]: ")
if command == '' or command == 'n' or command == 'N':
    print("No changes written.")
    exit()
elif command == 'y' or command == 'Y':
    member = dict(id=temp_id, rfid=new_rfid, name=new_name, email=new_email, attendance_count=new_attendance_count, late_count=new_late_count, checked_in=new_checked_in, last_date=new_last_date, last_time=new_last_time)
    members.update(member, ['id'])
    exit()
else:
    print("Invalid option.  No changes written.")
    exit()

