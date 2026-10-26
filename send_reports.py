import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import db
from emailer import send_weekly_recap, send_daily_appointments

# run this from Windows Task Scheduler (or cron) so the reports go out on their own:
#   python send_reports.py daily    -> today's appointments
#   python send_reports.py weekly   -> reviews from the last 7 days

# the scheduler may start us from another folder, so work from this file's folder
# so .env and data/app.db are found
os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()
db.init_db()


def main():
    report = sys.argv[1] if len(sys.argv) > 1 else ""
    recipient = os.environ.get("REPORT_EMAIL", "")

    if report == "daily":
        send_daily_appointments(recipient, datetime.now().date().isoformat())
    elif report == "weekly":
        send_weekly_recap(recipient)
    else:
        print("usage: python send_reports.py daily|weekly")
        sys.exit(1)

    print(f"{report} report done")


if __name__ == "__main__":
    main()
