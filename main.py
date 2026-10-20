"""main.py - starts the Library Occupancy Tracker.

Flow:  gui.py -> integration.py -> database.py -> MySQL
main.py only wires the GUI to the controller callbacks and launches it.
"""

import logging
import sys

import integration

log = logging.getLogger("library_occupancy_tracker")


def _show_startup_error(message):
    """Show a readable error in a small window (falls back to console)."""
    print("ERROR:", message, file=sys.stderr)
    try:
        import tkinter
        from tkinter import messagebox
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showerror("Library Occupancy Tracker", message)
        root.destroy()
    except Exception:
        pass


def _launch_gui(callbacks):
    """Start the Tkinter GUI. Adjust ONLY this function if Chandru's gui.py
    uses a different entry point."""
    import gui

    if hasattr(gui, "run_app"):          # def run_app(**callbacks)
        return gui.run_app(**callbacks)
    if hasattr(gui, "main"):             # def main(**callbacks)
        return gui.main(**callbacks)
    for name in ("App", "LibraryApp", "MainApp", "Application"):
        if hasattr(gui, name):           # class App(tk.Tk): __init__(**callbacks)
            return getattr(gui, name)(**callbacks).mainloop()
    raise RuntimeError(
        "gui.py has no entry point. Ask Chandru for the function or class "
        "that starts the window, then edit _launch_gui() in main.py.")


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    # Fail early with a readable message if the database is not ready.
    try:
        integration.get_occupancy_callback()
    except integration.IntegrationError as err:
        _show_startup_error(
            f"{err}\n\nCheck that MySQL is running, schema.sql was loaded "
            "and your settings in config.py / .env are correct.")
        return 1

    try:
        _launch_gui(integration.get_callbacks())
    except Exception as err:
        log.exception("Application failed to start")
        _show_startup_error(f"The application could not start: {err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

