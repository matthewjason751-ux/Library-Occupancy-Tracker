"""integration.py - controller layer.

Flow:  gui.py -> integration.py -> database.py -> MySQL

The GUI only calls the *_callback functions below. This module is the only
place that imports database.py. It contains no SQL.
"""

import logging

import config
import database

try:  # only used to recognise MySQL failures; the app still works without it
    from mysql.connector import Error as _MySQLError
except Exception:  # pragma: no cover
    class _MySQLError(Exception):
        pass

log = logging.getLogger(__name__)

# Single source of truth comes from config.py; these defaults only apply if
# config.py does not define the names yet.
ZONE_NAMES = tuple(getattr(config, "ZONE_NAMES",
                           ("Silent", "General", "Discussion", "Computer")))
ALERT_THRESHOLD = float(getattr(config, "ALERT_THRESHOLD", 0.90))

# Keys Nishi's get_zone_occupancy() rows may use (first match wins).
_ID_KEYS = ("zone_id", "id")
_NAME_KEYS = ("zone_name", "name", "zone")
_CAPACITY_KEYS = ("capacity", "max_capacity")
_OCCUPIED_KEYS = ("occupied", "current_count", "current_occupancy",
                  "occupancy", "active_visits", "current", "count")


class IntegrationError(ValueError):
    """Readable error message meant to be shown directly in the GUI."""


# ---------------------------------------------------------------- helpers

def _call_db(func, *args, error_message):
    """Call a database helper and translate failures into readable errors."""
    try:
        return func(*args)
    except IntegrationError:
        raise
    except ValueError as exc:  # business rule from database.py (duplicate etc.)
        raise IntegrationError(str(exc)) from exc
    except _MySQLError as exc:
        log.exception("MySQL error in %s", getattr(func, "__name__", func))
        raise IntegrationError(
            "Cannot reach the database. Please check that MySQL is running "
            "and try again.") from exc
    except Exception as exc:
        log.exception("Unexpected error in %s", getattr(func, "__name__", func))
        raise IntegrationError(error_message) from exc


def _first(row, keys):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def _load_zones():
    """Return {lower-case zone name: {zone_id, name, capacity, occupied}}."""
    rows = _call_db(database.get_zone_occupancy,
                    error_message="Could not load zone occupancy.")
    zones = {}
    for row in rows or []:
        if not isinstance(row, dict):
            raise IntegrationError(
                "Unexpected data from the database (zone rows must be dicts).")
        name = _first(row, _NAME_KEYS)
        zone_id = _first(row, _ID_KEYS)
        capacity = _first(row, _CAPACITY_KEYS)
        occupied = _first(row, _OCCUPIED_KEYS)
        if name is None or zone_id is None or capacity is None or occupied is None:
            raise IntegrationError(
                "Zone data from the database is missing a field "
                "(need zone id, name, capacity and occupied count).")
        zones[str(name).strip().lower()] = {
            "zone_id": zone_id,
            "name": str(name).strip(),
            "capacity": int(capacity),
            "occupied": int(occupied),
        }
    return zones


def _find_zone(zones, zone_name):
    key = str(zone_name or "").strip().lower()
    if key not in {n.lower() for n in ZONE_NAMES}:
        raise IntegrationError(
            "Please choose a valid zone: " + ", ".join(ZONE_NAMES) + ".")
    if key not in zones:
        raise IntegrationError(
            f"Zone '{zone_name}' was not found in the database. "
            "Run schema.sql to create the zones.")
    return zones[key]


def _clean_id(student_id):
    student_id = str(student_id or "").strip()
    if not student_id:
        raise IntegrationError("Please enter your student ID.")
    return student_id


# -------------------------------------------------------------- callbacks

def login_callback(student_id, password):
    """Return the student dict (without password) or None if credentials
    are wrong. Raises IntegrationError for empty input or database failure."""
    student_id = _clean_id(student_id)
    if not password:
        raise IntegrationError("Please enter your password.")
    student = _call_db(database.authenticate_student, student_id, password,
                       error_message="Login failed because of a database problem.")
    if not student:
        return None
    student = dict(student)
    student.pop("password", None)
    return student


def get_occupancy_callback():
    """Return live occupancy in the format the GUI/charts expect."""
    zones = _load_zones()
    result = {}
    for name in ZONE_NAMES:
        zone = _find_zone(zones, name)
        result[name] = {
            "capacity": zone["capacity"],
            "occupied": zone["occupied"],
            "threshold": ALERT_THRESHOLD,
        }
    return result


def check_in_callback(student_id, zone_name):
    """Check a student into a zone. Returns a success dict or raises
    IntegrationError."""
    student_id = _clean_id(student_id)
    zone = _find_zone(_load_zones(), zone_name)
    if zone["occupied"] >= zone["capacity"]:
        raise IntegrationError(
            f"The {zone['name']} zone is full. Please choose another zone.")
    visit_id = _call_db(database.check_in, student_id, zone["zone_id"],
                        error_message="Check-in failed because of a database problem.")
    return {"success": True, "visit_id": visit_id,
            "message": f"Checked in to {zone['name']}."}


def check_out_callback(student_id):
    """Check a student out. Returns a success dict or raises IntegrationError."""
    student_id = _clean_id(student_id)
    visit_id = _call_db(database.check_out, student_id,
                        error_message="Check-out failed because of a database problem.")
    return {"success": True, "visit_id": visit_id,
            "message": "Checked out successfully."}


# charts.py gets the same freshly loaded occupancy data from the controller.
get_chart_data_callback = get_occupancy_callback


def get_callbacks():
    """Convenience bundle for main.py when building the GUI."""
    return {
        "login_callback": login_callback,
        "get_occupancy_callback": get_occupancy_callback,
        "check_in_callback": check_in_callback,
        "check_out_callback": check_out_callback,
    }


if __name__ == "__main__":
    # Console smoke test (no GUI). Needs MySQL running and schema.sql loaded.
    logging.basicConfig(level=logging.INFO)
    try:
        print("login:", login_callback("DEMO001", "demo123"))
        print("before:", get_occupancy_callback())
        print(check_in_callback("DEMO001", "Silent"))
        print("after check-in:", get_occupancy_callback())
        print(check_out_callback("DEMO001"))
        print("after check-out:", get_occupancy_callback())
    except IntegrationError as err:
        print("ERROR:", err)
