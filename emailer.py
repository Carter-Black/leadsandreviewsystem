import os
import html
import resend
import db


def is_dry_run():
    # dry run is the default so nothing sends by accident, set EMAIL_DRY_RUN=0 to really send
    return os.environ.get("EMAIL_DRY_RUN", "1") != "0"


def sender():
    # onboarding@resend.dev only works for sending to your own Resend account,
    # set EMAIL_FROM to an address on a verified domain to send anywhere else
    return os.environ.get("EMAIL_FROM", "onboarding@resend.dev")


def clean(value):
    # escapes anything typed into the forms so it can't inject html into the email
    return html.escape(value or "")


def build_test_email(recipient):
    return {
        "from": sender(),
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
        "from": sender(),
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
        "from": sender(),
        "to": [recipient],
        "subject": f"Appointments for {target_date}",
        "html": f"<h1>Appointments for {target_date}</h1>" + body,
    }


def build_new_lead_email(recipient, appointment):
    # appointment can be the submitted form or a dict with the same keys
    name = clean(appointment.get("customer_name"))
    body = ("<table border='1' cellpadding='6'>"
            f"<tr><th>Name</th><td>{name}</td></tr>"
            f"<tr><th>Phone</th><td>{clean(appointment.get('phone'))}</td></tr>"
            f"<tr><th>Email</th><td>{clean(appointment.get('email'))}</td></tr>"
            f"<tr><th>Service</th><td>{clean(appointment.get('service'))}</td></tr>"
            f"<tr><th>Date</th><td>{clean(appointment.get('date'))}</td></tr>"
            f"<tr><th>Time</th><td>{clean(appointment.get('time'))}</td></tr>"
            f"<tr><th>Notes</th><td>{clean(appointment.get('notes'))}</td></tr>"
            "</table>")

    return {
        "from": sender(),
        "to": [recipient],
        # subject is plain text not html, so it doesn't need escaping
        "subject": f"New lead: {appointment.get('customer_name') or 'unknown'}",
        "html": f"<h1>New lead: {name}</h1>" + body,
    }


# ratings at or below this count as bad and get an alert right away
BAD_REVIEW_RATING = 2


def is_bad_review(rating):
    return rating <= BAD_REVIEW_RATING


def build_bad_review_email(recipient, author, rating, source, text):
    return {
        "from": sender(),
        "to": [recipient],
        "subject": f"Bad review alert: {rating}/5 from {author}",
        "html": (f"<h1>Bad review alert</h1>"
                 f"<p><b>{clean(author)}</b> left a {rating}/5 review via {clean(source)}:</p>"
                 f"<blockquote>{clean(text)}</blockquote>"
                 "<p>You may want to reply soon.</p>"),
    }


def send_email(message):
    if is_dry_run():
        print("DRY RUN, email not sent:", message)
        return message

    if not message["to"][0]:
        raise ValueError("REPORT_EMAIL is not set")

    # key is read here instead of at import so the app can start without it
    if not os.environ.get("RESEND_API_KEY"):
        raise ValueError("RESEND_API_KEY is not set")
    resend.api_key = os.environ["RESEND_API_KEY"]
    return resend.Emails.send(message)


def send_test_email(recipient):
    return send_email(build_test_email(recipient))


def send_weekly_recap(recipient, days=7):
    return send_email(build_weekly_recap_email(recipient, days))


def send_daily_appointments(recipient, target_date):
    return send_email(build_daily_appointments_email(recipient, target_date))


def send_new_lead_alert(recipient, appointment):
    return send_email(build_new_lead_email(recipient, appointment))


def send_bad_review_alert(recipient, author, rating, source, text):
    return send_email(build_bad_review_email(recipient, author, rating, source, text))
