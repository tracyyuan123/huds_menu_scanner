"""
Email Demo -- proof that the notifier can send emails
CS32 Final Project -- Tracy Yuan

This is a standalone script that sends a test email via Gmail SMTP
using an App Password. Run it to verify email delivery works.

Setup:
    1. Enable 2-Step Verification at myaccount.google.com/security
    2. Create an App Password at myaccount.google.com/apppasswords
    3. Copy .env.example to .env and fill in your credentials
"""

import os
import smtplib
from email.mime.text import MIMEText


def load_env():
    """Load variables from .env file into os.environ."""
    env_path = os.path.join(os.path.dirname(__file__) or ".", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    load_env()

    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    to_email = os.environ.get("NOTIFY_EMAIL", gmail_address)

    if not gmail_address or not gmail_password:
        print("ERROR: Create a .env file with GMAIL_ADDRESS and GMAIL_APP_PASSWORD")
        print("       (see .env.example)")
        return

    # Build a simple test email
    # MIME (Multipurpose Internet Mail Extensions) is a standard for formatting email messages
    msg = MIMEText("This is a test from the HUDS Menu Scanner project.")
    msg["Subject"] = "HUDS Menu Scanner -- Test Email"
    msg["From"] = gmail_address
    msg["To"] = to_email

    # Send via Gmail SMTP
    print(f"Sending test email to {to_email}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server: # handles network communication with Gmail's SMTP server
        server.login(gmail_address, gmail_password)
        server.sendmail(gmail_address, to_email, msg.as_string())

    print("Email sent successfully!")


if __name__ == "__main__":
    main()
