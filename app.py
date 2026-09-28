from flask import Flask, render_template, request, redirect, url_for
import os
import db
from emailer import send_test_email

app = Flask(__name__)

# creates the tables if they don't exist yet, safe to call every time the app starts
db.init_db()


@app.route("/")
@app.route("/dashboard")
def dashboard():
    reviews = db.get_new_reviews()
    appointments = db.get_appointments_this_week()
    return render_template("dashboard.html", reviews=reviews, appointments=appointments)


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


@app.route("/add-appointment", methods=["GET", "POST"], endpoint="add_appointment")
def add_appointment():
    if request.method == "POST":
        db.add_appointment(
            request.form["customer_name"],
            request.form["service"],
            request.form["date"],
            request.form["time"],
            request.form.get("notes", "")
        )
        return redirect(url_for("dashboard"))
    return render_template("add_appointment.html")

@app.route("/test-email", methods=["POST"])
def test_email():
    recipient = os.environ["REPORT_EMAIL"]
    send_test_email(recipient)
    return "Test email sent"


if __name__ == "__main__":
    app.run(debug=True)
