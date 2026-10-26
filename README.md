# University Library Occupancy Tracker

The University Library Occupancy Tracker is a Python desktop application developed using Tkinter, MySQL, and Matplotlib.

The application helps students and library staff monitor the current occupancy of different library zones.

## Project Objective

The main objective of this project is to provide live information about library occupancy so that students can choose suitable zones and avoid overcrowded areas.

The system records student check-ins and check-outs and updates the occupancy count automatically.

## Library Zones

The application contains four library zones:

- Silent Zone
- General Zone
- Discussion Zone
- Computer Zone

Each zone has its own capacity and current occupancy count.

## Main Features

### Student Login

Students log in using their student ID and password. Login details are verified through the MySQL database.

### Live Occupancy

The dashboard displays:

- Zone name
- Zone capacity
- Current number of students
- Occupancy status

### Student Check-in

Students can check into an available library zone.

The system:

- Records the student ID
- Records the selected zone
- Stores the check-in time
- Updates the zone occupancy
- Prevents duplicate check-ins
- Rejects check-in when a zone is full

### Student Check-out

Students can check out when they leave the library.

The system:

- Records the check-out time
- Decreases the zone occupancy
- Updates the dashboard
- Prevents checkout when no active visit exists

### Current Visit Status

The application shows whether the logged-in student is currently checked in.

It displays:

- Current zone
- Check-in time
- Not checked-in message

### Capacity Status

The application displays the status of each zone:

- Normal
- Medium
- High
- Full

The status is calculated using the current occupancy and zone capacity.

### Occupancy Alerts

The system shows alerts when a zone is close to its maximum capacity.

A full zone does not allow new check-ins.

### Occupancy Chart

Matplotlib is used to display a comparison between:

- Zone capacity
- Current occupancy

The chart refreshes after check-in and check-out actions.

### Check-out Reminder

If a student closes the application while still checked in, the application displays a reminder before closing.

## Application Architecture
gui.py
   ↓
integration.py
   ↓
database.py
   ↓
MySQL

