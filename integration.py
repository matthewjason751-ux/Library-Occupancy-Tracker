"""Controller layer for the Library Occupancy Tracker.

Flow:
gui.py → integration.py → database.py → MySQL

The GUI calls only the callback functions in this file.
This file contains no SQL code.
"""

import logging

import config
import database

try:
    from mysql.connector import Error as _MySQLError
except Exception:
    class _MySQLError(Exception):
        pass


log = logging.getLogger(__name__)

# Shared settings are read from config.py.
ZONE_NAMES = tuple(
    getattr(
        config,
        "ZONE_NAMES",
        ("Silent", "General", "Discussion", "Computer")
    )
)

ALERT_THRESHOLD = float(
    getattr(config, "ALERT_THRESHOLD", 0.90)
)

# Supported database field names.
_ID_KEYS = ("zone_id", "id")
_NAME_KEYS = ("zone_name", "name", "zone")
_CAPACITY_KEYS = ("capacity", "max_capacity")
_OCCUPIED_KEYS = (
    "occupied",
    "current_count",
    "current_occupancy",
    "occupancy",
    "active_visits",
    "current",
    "count"
)


class IntegrationError(ValueError):
    """Readable error message for the GUI."""


def _call_db(func, *args, error_message):
    """Call a database function and convert errors into readable messages."""
    try:
        return func(*args)

    except IntegrationError:
        raise

    except ValueError as error:
        raise IntegrationError(str(error)) from error

    except _MySQLError as error:
        log.exception(
            "MySQL error in %s",
            getattr(func, "__name__", func)
        )
        raise IntegrationError(
            "Cannot reach the database. "
            "Please check that MySQL is running and try again."
        ) from error

    except Exception as error:
        log.exception(
            "Unexpected error in %s",
            getattr(func, "__name__", func)
        )
        raise IntegrationError(error_message) from error


def _first(row, keys):
    """Return the first available value from a database row."""
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]

    return None


def _load_zones():
    """Load and format zone occupancy data."""
    rows = _call_db(
        database.get_zone_occupancy,
        error_message="Could not load zone occupancy."
    )

    zones = {}

    for row in rows or []:
        if not isinstance(row, dict):
            raise IntegrationError(
                "Unexpected data from the database."
            )

        name = _first(row, _NAME_KEYS)
        zone_id = _first(row, _ID_KEYS)
        capacity = _first(row, _CAPACITY_KEYS)
        occupied = _first(row, _OCCUPIED_KEYS)

        if (
            name is None
            or zone_id is None
            or capacity is None
            or occupied is None
        ):
            raise IntegrationError(
                "Zone data is missing a required field."
            )

        zones[str(name).strip().lower()] = {
            "zone_id": zone_id,
            "name": str(name).strip(),
            "capacity": int(capacity),
            "occupied": int(occupied)
        }

    return zones


def _find_zone(zones, zone_name):
    """Find a valid zone by name."""
    key = str(zone_name or "").strip().lower()

    valid_zones = {name.lower() for name in ZONE_NAMES}

    if key not in valid_zones:
        raise IntegrationError(
            "Please choose a valid zone: "
            + ", ".join(ZONE_NAMES)
            + "."
        )

    if key not in zones:
        raise IntegrationError(
            f"Zone '{zone_name}' was not found in the database."
        )

    return zones[key]


def _clean_id(student_id):
    """Validate and clean a student ID."""
    student_id = str(student_id or "").strip()

    if not student_id:
        raise IntegrationError(
            "Please enter your student ID."
        )

    return student_id


def login_callback(student_id, password):
    """Authenticate a student."""
    student_id = _clean_id(student_id)

    if not password:
        raise IntegrationError(
            "Please enter your password."
        )

    student = _call_db(
        database.authenticate_student,
        student_id,
        password,
        error_message="Login failed because of a database problem."
    )

    if not student:
        return None

    student = dict(student)
    student.pop("password", None)

    return student


def get_occupancy_callback():
    """Return live occupancy data for the dashboard."""
    zones = _load_zones()
    result = {}

    for name in ZONE_NAMES:
        zone = _find_zone(zones, name)

        result[name] = {
            "capacity": zone["capacity"],
            "occupied": zone["occupied"],
            "threshold": ALERT_THRESHOLD
        }

    return result


def check_in_callback(student_id, zone_name):
    """Check a student into a selected zone."""
    student_id = _clean_id(student_id)
    zone = _find_zone(_load_zones(), zone_name)

    if zone["occupied"] >= zone["capacity"]:
        raise IntegrationError(
            f"The {zone['name']} zone is full. "
            "Please choose another zone."
        )

    visit_id = _call_db(
        database.check_in,
        student_id,
        zone["zone_id"],
        error_message="Check-in failed because of a database problem."
    )

    return {
        "success": True,
        "visit_id": visit_id,
        "message": f"Checked in to {zone['name']}."
    }


def check_out_callback(student_id):
    """Check a student out of the library."""
    student_id = _clean_id(student_id)

    visit_id = _call_db(
        database.check_out,
        student_id,
        error_message="Check-out failed because of a database problem."
    )

    return {
        "success": True,
        "visit_id": visit_id,
        "message": "Checked out successfully."
    }


def get_current_visit_callback(student_id):
    """Return the active visit for a student."""
    student_id = _clean_id(student_id)

    history = _call_db(
        database.get_history,
        1000,
        error_message="Could not load your current visit."
    )

    for visit in history or []:
        if (
            visit.get("student_id") == student_id
            and visit.get("check_out_time") is None
        ):
            return visit

    return None


# Chart data is loaded through the controller.
get_chart_data_callback = get_occupancy_callback


def get_callbacks():
    """Return all callbacks required by the application."""
    return {
        "login_callback": login_callback,
        "get_occupancy_callback": get_occupancy_callback,
        "check_in_callback": check_in_callback,
        "check_out_callback": check_out_callback,
        "get_current_visit_callback": get_current_visit_callback
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        print(
            "Login:",
            login_callback("DEMO001", "demo123")
        )

        print(
            "Occupancy:",
            get_occupancy_callback()
        )

    except IntegrationError as error:
        print("ERROR:", error)