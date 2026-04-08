# Dining Hall Menu Scanner & Email Notifier

A tool that automatically scans the Harvard University Dining Services (HUDS) menu each
morning, matches menu items against personal food preferences, and emails a
personalized summary of what to eat that day.

## What it does

- **Scrapes** the daily HUDS dining hall menu from the web
- **Matches** menu items against a configurable list of liked foods, dietary
restrictions, and keywords using string/fuzzy matching
- **Emails** a clean, readable summary organized by meal
- **Runs automatically** each morning before breakfast
