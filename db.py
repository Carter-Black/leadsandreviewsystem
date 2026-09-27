import sqlite3
from datetime import datetime, timedelta

DB_PATH = "data/app.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # column names here match what dashboard.html / add_review.html expect
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            rating INTEGER NOT NULL,
            source TEXT,
            text TEXT,
            review_date TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL
        )
    """)

    # column names here match what dashboard.html / add_appointment.html expect
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            service TEXT,
            date TEXT NOT NULL,
            time TEXT,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---- Reviews ----

def add_review(author, rating, source, text, review_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews (author, rating, source, text, review_date, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'new', ?)
    """, (author, rating, source, text, review_date, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_new_reviews():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reviews WHERE status = 'new' ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def mark_review_reviewed(review_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE reviews SET status = 'reviewed' WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()


def get_recent_reviews(days=7):
    # filters on created_at (when it was added to our system), not review_date,
    # so this reflects "new since last recap" rather than when the review happened
    conn = get_connection()
    cur = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    cur.execute("SELECT * FROM reviews WHERE created_at >= ? ORDER BY created_at DESC", (cutoff,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ---- Appointments (leads) ----

def add_appointment(customer_name, service, date, time, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO appointments (customer_name, service, date, time, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (customer_name, service, date, time, notes, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_appointments_for_date(target_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE date = ? ORDER BY time", (target_date,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_appointments_this_week():
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    cur.execute(
        "SELECT * FROM appointments WHERE date BETWEEN ? AND ? ORDER BY date, time",
        (today.isoformat(), week_end.isoformat())
    )
    rows = cur.fetchall()
    conn.close()
    return rows
