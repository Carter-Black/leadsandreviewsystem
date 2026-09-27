import os
from datetime import datetime, timedelta
import db

# using a throwaway test db so you don't pollute real data
db.DB_PATH = "data/test.db"
if os.path.exists(db.DB_PATH):
    os.remove(db.DB_PATH)

db.init_db()

# reviews
today = datetime.now().date().isoformat()
db.add_review("Jane Doe", 5, "Google", "Great service!", today)
new_reviews = db.get_new_reviews()
assert len(new_reviews) == 1
assert new_reviews[0]["author"] == "Jane Doe"
assert new_reviews[0]["source"] == "Google"
assert new_reviews[0]["status"] == "new"

db.mark_review_reviewed(new_reviews[0]["id"])
assert len(db.get_new_reviews()) == 0
assert len(db.get_recent_reviews(days=7)) == 1

# appointments
appt_date = (datetime.now().date() + timedelta(days=2)).isoformat()
db.add_appointment("John Smith", "Haircut", appt_date, "4:00", "Wants a quote")
todays = db.get_appointments_for_date(appt_date)
assert len(todays) == 1
assert todays[0]["customer_name"] == "John Smith"
assert todays[0]["service"] == "Haircut"

week = db.get_appointments_this_week()
assert len(week) == 1

print("All db.py tests passed.")

# print everything currently in the test db
conn = db.get_connection()
cur = conn.cursor()

print("\nREVIEWS:")
cur.execute("SELECT * FROM reviews")
for row in cur.fetchall():
    print(dict(row))

print("\nAPPOINTMENTS:")
cur.execute("SELECT * FROM appointments")
for row in cur.fetchall():
    print(dict(row))

conn.close()
