import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]


def send_test_email(recipient):
    return resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [recipient],
        "subject": "Test business report",
        "html": "<h1>Email is working</h1><p>Your report system is connected.</p>",
    })