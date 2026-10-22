"""Starts the Library Occupancy Tracker."""

import logging
import sys

import integration

log = logging.getLogger("library_occupancy_tracker")


def _show_startup_error(message):
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
    import gui

    if hasattr(gui, "run_app"):
        return gui.run_app(**callbacks)

    if hasattr(gui, "main"):
        return gui.main(**callbacks)

    for name in ("App", "LibraryApp", "MainApp", "Application"):
        if hasattr(gui, name):
            return getattr(gui, name)(**callbacks).mainloop()

    if hasattr(gui, "window"):
        gui.window.mainloop()
        return

    raise RuntimeError("Could not find a GUI entry point.")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )

    try:
        integration.get_occupancy_callback()
    except integration.IntegrationError as error:
        _show_startup_error(
            f"{error}\n\n"
            "Check that MySQL is running and the database is configured."
        )
        return 1

    try:
        _launch_gui(integration.get_callbacks())
    except Exception as error:
        log.exception("Application failed to start")
        _show_startup_error(f"The application could not start:\n{error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())