from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import db
from datetime import datetime
from emailer import send_test_email, send_weekly_recap, send_daily_appointments, is_dry_run

# loads RESEND_API_KEY, REPORT_EMAIL and EMAIL_DRY_RUN from the .env file if it has them
load_dotenv()

app = Flask(__name__)

# creates the tables if they don't exist yet, safe to call every time the app starts
db.init_db()


@app.route("/")
@app.route("/dashboard")
def dashboard():
    reviews = db.get_new_reviews()
    reviewed_reviews = db.get_reviewed_reviews()
    appointments = db.get_appointments_this_week()
    return render_template("dashboard.html", reviews=reviews, reviewed_reviews=reviewed_reviews, appointments=appointments)


@app.route("/add-review", methods=["GET", "POST"], endpoint="add_review")
def add_review():
    if request.method == "POST":
        db.add_review(
            request.form["author"],
            int(request.form["rating"]),
            request.form["source"],
            request.form["text"],
            request.form["date"]
        )
        return redirect(url_for("dashboard"))
    return render_template("add_review.html")


# marks a review as handled so it drops off the dashboard's "new" list
@app.route("/reviews/<int:review_id>/reviewed", methods=["POST"])
def mark_reviewed(review_id):
    db.mark_review_reviewed(review_id)
    return redirect(url_for("dashboard"))


@app.route("/add-appointment", methods=["GET", "POST"], endpoint="add_appointment")
def add_appointment():
    if request.method == "POST":
        db.add_appointment(
            request.form["customer_name"],
            request.form["phone"],
            request.form["email"],
            request.form["service"],
            request.form["date"],
            request.form["time"],
            request.form.get("notes", "")
        )
        return redirect(url_for("dashboard"))
    return render_template("add_appointment.html")


@app.route("/test-email", methods=["POST"])
def test_email():
    recipient = os.environ.get("REPORT_EMAIL", "")
    send_test_email(recipient)
    if is_dry_run():
        return "Dry run, no email sent. The message was printed in the terminal."
    return "Test email sent"


@app.route("/send-weekly-recap", methods=["POST"])
def weekly_recap():
    recipient = os.environ.get("REPORT_EMAIL", "")
    send_weekly_recap(recipient)
    if is_dry_run():
        return "Dry run, no email sent. The weekly recap was printed in the terminal."
    return "Weekly recap sent"


@app.route("/send-daily-appointments", methods=["POST"])
def daily_appointments():
    recipient = os.environ.get("REPORT_EMAIL", "")
    # same YYYY-MM-DD format the appointment form's date picker saves
    today = datetime.now().date().isoformat()
    send_daily_appointments(recipient, today)
    if is_dry_run():
        return "Dry run, no email sent. Today's appointments were printed in the terminal."
    return "Today's appointments sent"


if __name__ == "__main__":
    app.run(debug=True)
