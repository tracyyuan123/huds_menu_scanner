"""
Email Sender
CS32 Final Project
Tracy Yuan

Provides a reusable send_email function. Credentials are loaded from a .env
file (GMAIL_ADDRESS, GMAIL_APP_PASSWORD).

Setup:
    1. Enable 2-Step Verification at myaccount.google.com/security
    2. Create an App Password at myaccount.google.com/apppasswords
    3. Copy .env.example to .env and fill in your credentials
"""

import os
import smtplib
from email.mime.text import MIMEText


def load_env(env_path=None):
    """Load variables from .env file into os.environ."""
    if env_path is None:
        env_path = os.path.join(os.path.dirname(__file__) or ".", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def send_email(subject, body, env_path=None):
    """Send an email via Gmail SMTP.

    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env file.
    Returns True if sent successfully, False otherwise.
    """
    load_env(env_path)

    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    to_email = os.environ.get("NOTIFY_EMAIL", gmail_address)

    if not gmail_address or not gmail_password:
        print("  WARNING: Email credentials not found in .env file.")
        print("  Skipping email. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD.")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_password)
            server.sendmail(gmail_address, to_email, msg.as_string())
        print(f"  Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"  ERROR sending email: {e}")
        return False


if __name__ == "__main__":
    # Quick test: send a test email
    load_env()
    send_email(
        subject="HUDS Menu Scanner -- Test Email",
        body="This is a test from the HUDS Menu Scanner project.",
    )
