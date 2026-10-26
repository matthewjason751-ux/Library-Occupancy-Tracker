#gui.py
import tkinter as tk
from tkinter import messagebox
from charts import show_occupancy_chart
from integration import (
    login_callback,
    get_occupancy_callback,
    check_in_callback,
    check_out_callback,
    get_current_visit_callback,
    IntegrationError
)
window = tk.Tk()
window.title("University Library Occupancy Portal")
window.geometry("1100x700")
window.configure(bg="#f5f0e6")
student_id = None
dashboard_status_label = None
dashboard_frame = None
zones_frame = None
chart_frame = None
chart_canvas = None
current_visit_label = None
header= tk.Frame(window,bg="#8b0033", height = 70)
header.pack(fill="x")
header.pack_propagate(False)
title_label = tk.Label(
    header,
    text="UNIVERSITY LIBRARY OCCUPANCY PORTAL",
    bg="#8b0033",
    fg="white",
    font=("Arial", 18, "bold")
)
title_label.pack(side="left", padx=25, pady=20)
login_card = tk.Frame(
    window,
    bg="white",
    width=500,
    height=430,
    relief="solid",
    borderwidth = 1
)
login_card.pack(pady=70)
login_card.pack_propagate(False)

login_title = tk.Label(
    login_card,
    text = "Library System Login",
    bg="white",
    fg="#222222",
    font=("Times New Roman", 20, "bold"),
    justify="center"
)
login_title.pack(pady=(30, 25))
student_label = tk.Label(
    login_card,
    text = "Student ID / Register No:",
    bg = "white",
    fg = "#222222",
    font = ("Arial", 12)
)
student_label.pack(anchor="w", padx=55)
student_entry = tk.Entry(
    login_card,
    width=35,
    font=("Arial", 12),
    bg="#f5f0e6"
)
student_entry.pack(pady=(5, 15))
password_label = tk.Label(
    login_card,
    text="Password:",
    bg="white",
    font=("Arial", 12)
)
password_label.pack(anchor="w", padx=55)
password_entry = tk.Entry(
    login_card,
    width=35,
    font=("Arial", 12),
    bg="#f5f0e6",
    show="*"
)
password_entry.pack(pady=(5, 20))

def show_dashboard():
    login_card.pack_forget()

    global dashboard_frame
    global dashboard_status_label
    global chart_frame
    global chart_canvas

    dashboard_frame = tk.Frame(
        window,
        bg="#f5f0e6"
    )

    dashboard_frame.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=30
    )

    dashboard_top = tk.Frame(dashboard_frame, bg="#f5f0e6")
    dashboard_top.pack(fill="x", pady=(0, 10))

    dashboard_title = tk.Label(
        dashboard_top,
        text="MAIN DASHBOARD",
        bg="#f5f0e6",
        font=("Arial", 22, "bold")
    )
    dashboard_title.pack(side="left")

    check_out_button = tk.Button(
        dashboard_top,
        text="CHECK OUT",
        command=check_out_student,
        bg="#8b0033",
        fg="white",
        activebackground="#650025",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        padx=14,
        pady=5
    )
    check_out_button.pack(side="right")

    dashboard_status_label = tk.Label(
        dashboard_frame,
        text="Ready for check-in or check-out.",
        bg="#f5f0e6",
        fg="#333333",
        font=("Arial", 12)
    )

    dashboard_status_label.pack(anchor="w", pady=10)

    global current_visit_label

    current_visit_label = tk.Label(
    dashboard_frame,
    text="Checking current visit...",
    bg="#f5f0e6",
    fg="#555555",
    font=("Arial", 11, "italic")
    )  

    current_visit_label.pack(anchor="w")

    global zones_frame
    zones_frame = tk.Frame(
        dashboard_frame,
        bg="#f5f0e6"
    )

    zones_frame.pack(fill="x")

    chart_frame = tk.Frame(
        dashboard_frame,
        bg="white",
        height=360
    )

    chart_frame.pack(
        fill="both",
        expand=True,
        pady=10
    )

    chart_frame.pack_propagate(False)

    refresh_dashboard()
    refresh_current_visit()

def refresh_current_visit():
    if current_visit_label is None:
        return

    try:
        visit = get_current_visit_callback(student_id)

        if visit:
            current_visit_label.config(
                text=(
                    f"Currently checked in to {visit['zone_name']} | "
                    f"Check-in time: {visit['check_in_time']}"
                ),
                fg="green"
            )
        else:
            current_visit_label.config(
                text="You are not currently checked in.",
                fg="#555555"
            )

    except IntegrationError as error:
        current_visit_label.config(
            text=f"Could not load current visit: {error}",
            fg="red"
        )

def refresh_dashboard():
    global chart_canvas

    for widget in zones_frame.winfo_children():
        widget.destroy()

    occupancy_data = get_occupancy_callback()

    for zone_name, values in occupancy_data.items():
        capacity = values["capacity"]
        occupied = values["occupied"]
        threshold = values["threshold"]

        if occupied >= capacity:
            status = "FULL"
            status_color = "red"
        elif occupied / capacity >= threshold:
            status = "HIGH"
            status_color = "orange"
        else:
            status = "NORMAL"
            status_color = "green"

        zone_card = tk.Frame(
            zones_frame,
            bg="white",
            width=220,
            height=200,
            relief="solid",
            borderwidth=1
        )

        zone_card.pack(
            side="left",
            expand=True,
            fill="both",
            padx=8
        )

        zone_card.pack_propagate(False)

        tk.Label(
            zone_card,
            text=f"{zone_name.upper()} ZONE",
            bg="white",
            font=("Arial", 13, "bold")
        ).pack(pady=(20, 12))

        tk.Label(
            zone_card,
            text=f"Capacity: {capacity}",
            bg="white",
            font=("Arial", 12)
        ).pack()

        tk.Label(
            zone_card,
            text=f"Current: {occupied}",
            bg="white",
            font=("Arial", 12)
        ).pack(pady=5)

        tk.Label(
            zone_card,
            text=f"Status: {status}",
            bg="white",
            fg=status_color,
            font=("Arial", 12, "bold")
        ).pack()

        check_in_button = tk.Button(
            zone_card,
            text="CHECK IN",
            command=lambda selected_zone=zone_name:
                check_in_student(selected_zone)
        )

        check_in_button.pack(pady=8)

    if chart_canvas is not None:
        chart_canvas.get_tk_widget().destroy()

    chart_canvas = show_occupancy_chart(
        chart_frame,
        get_occupancy_callback()
    )

def check_in_student(zone):
    try:
        result = check_in_callback(student_id, zone)

        dashboard_status_label.config(
            text=result.get("message", f"Checked in to {zone}."),
            fg="green"
        )

        refresh_dashboard()
        refresh_current_visit()

    except IntegrationError as error:
        dashboard_status_label.config(
            text=f"Check-in failed: {error}",
            fg="red"
        )

def check_out_student():
    try:
        result = check_out_callback(student_id)

        dashboard_status_label.config(
            text=result.get("message", "Checked out successfully."),
            fg="green"
        )

        refresh_dashboard()
        refresh_current_visit()

    except IntegrationError as error:
        dashboard_status_label.config(
            text=f"Check-out failed: {error}",
            fg="red"
        )
def login_user():
    global student_id

    student_id = student_entry.get().strip()
    password = password_entry.get()

    if student_id == "" or password == "":
        status_label.config(
            text="Status: Please enter all fields.",
            fg="red"
        )
        return

    try:
        result = login_callback(student_id, password)
    except IntegrationError as error:
        status_label.config(
            text=f"Login failed: {error}",
            fg="red"
        )
        return

    if result:
        status_label.config(
            text="Status: Login successful.",
            fg="green"
        )
        window.after(500, show_dashboard)
    else:
        status_label.config(
            text="Status: Invalid student ID or password.",
            fg="red"
        )

login_button = tk.Button(
    login_card,
    text="LOG IN",
    command=login_user,
    width=30,
    height=2,
    bg="#8b0033",
    fg="white",
    activebackground="#650025",
    activeforeground="white",
    font=("Arial", 12, "bold"),
    relief="flat"
)
login_button.pack()
status_label = tk.Label(
    login_card,
    text="Status: Please enter your credentials.",
    bg="white",
    fg="#333333",
    font=("Arial", 11)
)
status_label.pack(pady=18)

def handle_window_close():
    if student_id:
        try:
            visit = get_current_visit_callback(student_id)

            if visit and not messagebox.askyesno(
                "Active check-in",
                "You are still checked in. Close without checking out?"
            ):
                return

        except IntegrationError:
            pass

    window.destroy()


window.protocol("WM_DELETE_WINDOW", handle_window_close)

if __name__ == "__main__":
    window.mainloop()
