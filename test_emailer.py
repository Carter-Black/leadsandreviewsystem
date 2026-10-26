import os
from datetime import datetime, timedelta

# dry run mode so this test never sends a real email or needs an API key
os.environ["EMAIL_DRY_RUN"] = "1"

import db
import emailer

assert emailer.is_dry_run()

# test email
message = emailer.send_test_email("someone@example.com")
assert message["to"] == ["someone@example.com"]
assert message["subject"] == "Test business report"
assert "Email is working" in message["html"]

# using a throwaway test db so you don't pollute real data
db.DB_PATH = "data/test_emailer.db"
if os.path.exists(db.DB_PATH):
    os.remove(db.DB_PATH)
db.init_db()

today = datetime.now().date()
today_str = today.isoformat()
tomorrow_str = (today + timedelta(days=1)).isoformat()

# weekly recap with no reviews yet
recap = emailer.build_weekly_recap_email("owner@example.com")
assert "No new reviews" in recap["html"]

# weekly recap with reviews, one has html in it to check it gets escaped
db.add_review("Jane Doe", 5, "Google", "Great service!", today_str)
db.add_review("Sam Lee", 3, "Yelp", "<script>alert(1)</script>", today_str)
recap = emailer.build_weekly_recap_email("owner@example.com")
assert recap["to"] == ["owner@example.com"]
assert recap["subject"] == "Weekly review recap"
assert "2 reviews" in recap["html"]
assert "average rating 4.0" in recap["html"]
assert "Jane Doe" in recap["html"]
assert "<script>" not in recap["html"]
assert "&lt;script&gt;" in recap["html"]

# daily appointments, one today and one tomorrow
assert "No appointments" in emailer.build_daily_appointments_email("owner@example.com", today_str)["html"]
db.add_appointment("John Smith", "949-555-1234", "john@example.com",
                    "Haircut", today_str, "4:00", "Wants a quote")
db.add_appointment("Mary Jones", "949-555-9999", "mary@example.com",
                    "Color", tomorrow_str, "10:00", "")
daily = emailer.build_daily_appointments_email("owner@example.com", today_str)
assert daily["subject"] == "Appointments for " + today_str
assert "John Smith" in daily["html"]
assert "949-555-1234" in daily["html"]
assert "Mary Jones" not in daily["html"]

# the send functions should hand back the message without sending in dry run
assert emailer.send_weekly_recap("owner@example.com")["subject"] == "Weekly review recap"
assert emailer.send_daily_appointments("owner@example.com", today_str)["to"] == ["owner@example.com"]

# sender defaults to the resend test address, EMAIL_FROM overrides it
os.environ.pop("EMAIL_FROM", None)
assert emailer.build_test_email("a@example.com")["from"] == "onboarding@resend.dev"
os.environ["EMAIL_FROM"] = "reports@mybusiness.com"
assert emailer.build_test_email("a@example.com")["from"] == "reports@mybusiness.com"
del os.environ["EMAIL_FROM"]

# new lead alert, built from the same keys the appointment form sends
lead = {"customer_name": "John Smith", "phone": "949-555-1234", "email": "john@example.com",
        "service": "Haircut", "date": today_str, "time": "4:00", "notes": "<b>call me</b>"}
alert = emailer.send_new_lead_alert("owner@example.com", lead)
assert alert["to"] == ["owner@example.com"]
assert alert["subject"] == "New lead: John Smith"
assert "949-555-1234" in alert["html"]
assert "Haircut" in alert["html"]
assert "<b>call me</b>" not in alert["html"]
assert "&lt;b&gt;call me&lt;/b&gt;" in alert["html"]

# notes is optional on the form, a missing one shouldn't break the email
del lead["notes"]
assert "John Smith" in emailer.build_new_lead_email("owner@example.com", lead)["html"]

# bad review alert only for ratings of 2 or less
assert emailer.is_bad_review(1)
assert emailer.is_bad_review(2)
assert not emailer.is_bad_review(3)
bad = emailer.send_bad_review_alert("owner@example.com", "Sam Lee", 1, "Yelp", "<i>awful</i>")
assert bad["to"] == ["owner@example.com"]
assert bad["subject"] == "Bad review alert: 1/5 from Sam Lee"
assert "Yelp" in bad["html"]
assert "<i>awful</i>" not in bad["html"]

print("All emailer.py tests passed. No email was sent.")
