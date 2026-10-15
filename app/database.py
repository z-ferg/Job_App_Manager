# database.py
# ------------------------------------------------------------------
# This file is the ONLY place in the project that talks to PostgreSQL.
# Why a separate file? The web page (app.py) stays simple: it just calls
# functions like add_student(). If a query is wrong, you know to look here.
# ------------------------------------------------------------------

# psycopg2 is the "driver": the library that lets Python send SQL to
# PostgreSQL and receive the results. Python cannot do this on its own.
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connection settings. Every value must match docker-compose.yml,
# otherwise PostgreSQL rejects the login.
DB_CONFIG = {
    "host": "localhost",        # the database is reached through this computer
    "port": 5433,               # the LEFT number in "5433:5432" (the outside port)
    "dbname": "studentdb",      # POSTGRES_DB
    "user": "student",          # POSTGRES_USER
    "password": "studentpassword",  # POSTGRES_PASSWORD
}


def get_connection():
    # Opens a new connection to PostgreSQL.
    # **DB_CONFIG unpacks the dictionary, same as writing
    # psycopg2.connect(host="localhost", port=5433, ...).
    url = os.environ.get("DATABASE_URL")
    if url and url != '':
        return psycopg2.connect(url)
    return psycopg2.connect(**DB_CONFIG)


def run_query(sql, params=None):
    """Run a SELECT and return (column_names, rows)."""
    conn = get_connection()
    try:
        # A cursor is the object that sends SQL and holds the results.
        # "with" closes the cursor automatically when the block ends.
        with conn.cursor() as cur:
            # params fills the %s placeholders safely (prevents SQL injection).
            cur.execute(sql, params)
            # cur.description describes the result columns; we keep the names
            # so the web page can show proper table headers.
            columns = [desc[0] for desc in cur.description]
            # fetchall() brings every result row back into Python as a list of tuples.
            rows = cur.fetchall()
        return columns, rows
    finally:
        # "finally" runs even if the query failed, so the connection is
        # always closed. Leaving connections open wastes database resources.
        conn.close()


def run_change(sql, params=None):
    """Run an INSERT/UPDATE/DELETE. Returns the number of rows affected."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            # rowcount = how many rows were changed. The page uses it to tell
            # the user "No student with that ID" when nothing matched.
            count = cur.rowcount
        # commit() makes the change permanent. PostgreSQL keeps changes in a
        # transaction until you commit; without this line they are thrown away.
        conn.commit()
        return count
    except Exception:
        # Something failed (e.g. a duplicate email). rollback() cancels the
        # half-finished change so the database is never left broken...
        conn.rollback()
        # ...and raise passes the error on to app.py, which shows a message.
        raise
    finally:
        conn.close()


# ---------- READ (the R in CRUD) ----------
def get_students():
    # ORDER BY gives a predictable order; without it rows can come back in any order.
    return run_query("SELECT student_id, name, email FROM student ORDER BY student_id;")


def search_students(keyword):
    # ILIKE = case-insensitive match. The % wildcards ("anything before/after")
    # go in the PARAMETER, not in the SQL string, so the query stays safe.
    return run_query(
        "SELECT student_id, name, email FROM student "
        "WHERE name ILIKE %s OR email ILIKE %s ORDER BY student_id;",
        (f"%{keyword}%", f"%{keyword}%"),
    )


# ---------- CREATE (the C in CRUD) ----------
def add_student(name, email):
    # We do not insert student_id: it is SERIAL, so PostgreSQL numbers it.
    # %s placeholders: NEVER paste user input into the SQL string yourself.
    return run_change(
        "INSERT INTO students (name, email) VALUES (%s, %s);",
        (name, email),
    )


# ---------- UPDATE (the U in CRUD) ----------
def update_student_email(student_id, new_email):
    # The WHERE clause is essential: without it, EVERY student's email changes.
    return run_change(
        "UPDATE students SET email = %s WHERE student_id = %s;",
        (new_email, student_id),
    )


# ---------- DELETE (the D in CRUD) ----------
def delete_student(student_id):
    # (student_id,) needs the trailing comma: it makes a one-item tuple.
    # ON DELETE CASCADE in init.sql also removes this student's enrollments.
    return run_change(
        "DELETE FROM student WHERE student_id = %s;",
        (student_id,),
    )


# ---------- JOIN (required feature) ----------
def get_enrollment_details():
    # Combines three tables so the user sees names instead of bare ID numbers.
    # s, e, c are short aliases for the table names.
    return run_query("""
        SELECT s.name, c.course_name, e.semester, e.grade
        FROM student s
        JOIN enrollments e ON s.student_id = e.student_id
        JOIN courses c     ON c.course_id  = e.course_id
        ORDER BY s.name;
    """)


# ---------- AGGREGATE (required feature) ----------
def get_course_counts():
    # COUNT + GROUP BY = one summary row per course.
    # LEFT JOIN keeps courses with zero students (a plain JOIN would hide them).
    return run_query("""
        SELECT c.course_name, COUNT(e.student_id) AS number_of_students
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id = e.course_id
        GROUP BY c.course_name
        ORDER BY number_of_students DESC;
    """)


# Self-test. This block runs ONLY when you type:  python app/database.py
# When app.py imports this file, it is skipped. Use it to check the
# connection works before building the web page.
if __name__ == "__main__":
    columns, rows = get_students()
    print(columns)
    for row in rows:
        print(row)