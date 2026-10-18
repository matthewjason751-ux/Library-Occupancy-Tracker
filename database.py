import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'library_tracker',
    'user': 'root',
    'password': 'Nishi938'  
}

def get_connection():
    """Establish and return a database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Database connection error: {e}")
        raise e

def authenticate_student(student_id, password):
    """Authenticate a student using student_id and password."""
    query = """
        SELECT student_id, full_name, is_active 
        FROM students 
        WHERE student_id = %s AND password = %s AND is_active = TRUE
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, (student_id, password))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_current_occupancy():
    """Returns (total_occupancy, total_capacity, available_slots)."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM visits WHERE check_out_time IS NULL")
        total_occupancy = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(capacity) FROM zones")
        total_capacity = cursor.fetchone()[0] or 0

        available = max(0, total_capacity - total_occupancy)
        return total_occupancy, total_capacity, available
    finally:
        cursor.close()
        conn.close()

def get_zone_occupancy():
    """Returns a list of zone dictionaries with current counts."""
    query = """
        SELECT z.zone_id, z.zone_name, z.capacity, 
               COUNT(v.visit_id) AS current_occupancy
        FROM zones z
        LEFT JOIN visits v ON z.zone_id = v.zone_id AND v.check_out_time IS NULL
        GROUP BY z.zone_id, z.zone_name, z.capacity
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def check_in(student_id, zone_id):
    """Checks in a student to a zone. Returns visit_id or raises ValueError."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT visit_id FROM visits WHERE student_id = %s AND check_out_time IS NULL", (student_id,))
        if cursor.fetchone():
            raise ValueError("Student is already checked into a zone.")

        cursor.execute("SELECT capacity FROM zones WHERE zone_id = %s", (zone_id,))
        zone = cursor.fetchone()
        if not zone:
            raise ValueError("Selected zone does not exist.")

        cursor.execute("SELECT COUNT(*) AS cnt FROM visits WHERE zone_id = %s AND check_out_time IS NULL", (zone_id,))
        current_zone_occ = cursor.fetchone()['cnt']

        if current_zone_occ >= zone['capacity']:
            raise ValueError("Selected zone is at full capacity.")

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_query = "INSERT INTO visits (student_id, zone_id, check_in_time) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (student_id, zone_id, now))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        conn.rollback()
        raise ValueError(f"Database error during check-in: {e}")
    finally:
        cursor.close()
        conn.close()

def check_out(student_id):
    """Checks out an active student. Returns closed visit_id or raises ValueError."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT visit_id FROM visits WHERE student_id = %s AND check_out_time IS NULL", (student_id,))
        active_visit = cursor.fetchone()

        if not active_visit:
            raise ValueError("No active check-in found for this student.")

        visit_id = active_visit['visit_id']
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query = "UPDATE visits SET check_out_time = %s WHERE visit_id = %s"
        cursor.execute(update_query, (now, visit_id))
        conn.commit()
        return visit_id
    except Error as e:
        conn.rollback()
        raise ValueError(f"Database error during check-out: {e}")
    finally:
        cursor.close()
        conn.close()

def get_history(limit=100):
    """Returns a list of visit dictionaries."""
    query = """
        SELECT v.visit_id, s.student_id, s.full_name, z.zone_name, 
               v.check_in_time, v.check_out_time
        FROM visits v
        JOIN students s ON v.student_id = s.student_id
        JOIN zones z ON v.zone_id = z.zone_id
        ORDER BY v.check_in_time DESC
        LIMIT %s
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_statistics(date=None):
    """Returns entries, exits, peak, and average counts."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if date:
            entry_sql = "SELECT COUNT(*) AS entries FROM visits WHERE DATE(check_in_time) = %s"
            exit_sql = "SELECT COUNT(*) AS exits FROM visits WHERE check_out_time IS NOT NULL AND DATE(check_out_time) = %s"
            params = (date,)
        else:
            entry_sql = "SELECT COUNT(*) AS entries FROM visits"
            exit_sql = "SELECT COUNT(*) AS exits FROM visits WHERE check_out_time IS NOT NULL"
            params = ()

        cursor.execute(entry_sql, params)
        entries = cursor.fetchone()['entries']

        cursor.execute(exit_sql, params)
        exits = cursor.fetchone()['exits']

        return {
            "entries": entries,
            "exits": exits,
            "peak": entries,
            "average": round(entries / 2, 1) if entries > 0 else 0
        }
    finally:
        cursor.close()
        conn.close()

def get_graph_data(date=None):
    """Returns timestamp and occupancy pairs for plotting."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT check_in_time AS ts, 1 AS chg 
            FROM visits 
            UNION ALL 
            SELECT check_out_time AS ts, -1 AS chg 
            FROM visits 
            WHERE check_out_time IS NOT NULL
            ORDER BY ts ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        running_occ = 0
        data_points = []
        for r in rows:
            running_occ += r['chg']
            data_points.append({
                "time": r['ts'],
                "occupancy": running_occ
            })
        return data_points
    finally:
        cursor.close()
        conn.close()