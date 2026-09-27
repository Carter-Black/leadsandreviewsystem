from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/dashboard")
def dashboard():
    reviews = []
    appointments = []
    return render_template("dashboard.html", reviews=reviews, appointments=appointments)


@app.route("/add-review", endpoint="add_review")
def add_review():
    return render_template("add_review.html")


@app.route("/add-appointment", endpoint="add_appointment")
def add_appointment():
    return render_template("add_appointment.html")


if __name__ == "__main__":
    app.run(debug=True)