import os
import html
import resend
import db


def is_dry_run():
    # dry run is the default so nothing sends by accident, set EMAIL_DRY_RUN=0 to really send
    return os.environ.get("EMAIL_DRY_RUN", "1") != "0"


def clean(value):
    # escapes anything typed into the forms so it can't inject html into the email
    return html.escape(value or "")


def build_test_email(recipient):
    return {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": "Test business report",
        "html": "<h1>Email is working</h1><p>Your report system is connected.</p>",
    }


def build_weekly_recap_email(recipient, days=7):
    # uses created_at (when the review was added), same as db.get_recent_reviews
    reviews = db.get_recent_reviews(days)

    if reviews:
        average = sum(r["rating"] for r in reviews) / len(reviews)
        word = "review" if len(reviews) == 1 else "reviews"
        items = ""
        for r in reviews:
            items += (f"<li><b>{clean(r['author'])}</b> {r['rating']}/5 via {clean(r['source'])}: "
                      f"{clean(r['text'])}</li>")
        body = (f"<p>{len(reviews)} {word} in the last {days} days, "
                f"average rating {average:.1f} out of 5.</p><ul>{items}</ul>")
    else:
        body = f"<p>No new reviews in the last {days} days.</p>"

    return {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": "Weekly review recap",
        "html": "<h1>Weekly review recap</h1>" + body,
    }


def build_daily_appointments_email(recipient, target_date):
    appointments = db.get_appointments_for_date(target_date)

    if appointments:
        rows = ""
        for a in appointments:
            rows += (f"<tr><td>{clean(a['time'])}</td><td>{clean(a['customer_name'])}</td>"
                     f"<td>{clean(a['service'])}</td><td>{clean(a['phone'])}</td>"
                     f"<td>{clean(a['email'])}</td><td>{clean(a['notes'])}</td></tr>")
        body = ("<table border='1' cellpadding='6'>"
                "<tr><th>Time</th><th>Customer</th><th>Service</th><th>Phone</th><th>Email</th><th>Notes</th></tr>"
                f"{rows}</table>")
    else:
        body = "<p>No appointments for this day.</p>"

    return {
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": f"Appointments for {target_date}",
        "html": f"<h1>Appointments for {target_date}</h1>" + body,
    }


def send_email(message):
    if is_dry_run():
        print("DRY RUN, email not sent:", message)
        return message

    if not message["to"][0]:
        raise ValueError("REPORT_EMAIL is not set")

    # key is read here instead of at import so the app can start without it
    resend.api_key = os.environ["RESEND_API_KEY"]
    return resend.Emails.send(message)


def send_test_email(recipient):
    return send_email(build_test_email(recipient))


def send_weekly_recap(recipient, days=7):
    return send_email(build_weekly_recap_email(recipient, days))


def send_daily_appointments(recipient, target_date):
    return send_email(build_daily_appointments_email(recipient, target_date))
