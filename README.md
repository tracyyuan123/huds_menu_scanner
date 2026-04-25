# Dining Hall Menu Scanner & Email Notifier

**CS32 Final Project by Tracy Yuan**

A tool that scrapes the Harvard University Dining Services (HUDS) menu each day, matches menu items against personal food preferences, and emails a personalized summary of what to eat.

## What It Does

1. **Scrapes** the daily HUDS dining hall menu from the FoodPro website using `requests` and `BeautifulSoup` (web scraping -- new skill learned for this project)
2. **Matches** menu items against a configurable list of liked/disliked foods using case-insensitive substring matching (dislikes override likes)
3. **Formats** a readable email body organized by meal (Breakfast, Lunch, Dinner)
4. **Emails** the report to your inbox via Gmail SMTP
5. **Saves** a local copy of the report as a `.txt` file

## Project Files

| File | Location | Purpose |
|------|----------|---------|
| `scrape_menu.py` | `FP_Design/` | Library module: scrapes FoodPro website + matches items against preferences |
| `send_email.py` | `FP_Design/` | Library module: sends emails via Gmail SMTP |
| `preferences.json` | `FP_Design/` | User food preferences config file |
| `.env` | `FP_Design/` | Gmail credentials (not committed -- see setup below) |
| `daily_notifier.py` | `FP_Status/` | Pipeline orchestrator: imports from the three modules above |
| `format_report.py` | `FP_Status/` | Formats matched results into a readable email body |

## Setup

### 1. Install dependencies

```
pip install requests beautifulsoup4
```

### 2. Configure food preferences

Edit `FP_Design/preferences.json` with your own liked and disliked foods:

```json
{
    "liked_foods": ["chicken", "salmon", "rice", "pasta", "cake"],
    "disliked_foods": ["cheese", "beets", "liver"]
}
```

### 3. Set up email credentials

1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Create an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Copy `.env.example` to `.env` and fill in your credentials:

```
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
NOTIFY_EMAIL=your_email@gmail.com
```

**Never commit `.env` to git** It contains your Gmail **password** and is already in `.gitignore`.

## How to Run

From the `FP_Status/` directory:

```
python3 daily_notifier.py
```

The script will prompt you to pick a dining hall:
1. Annenberg
2. Quincy House
3. House (except Quincy)

It then scrapes the menu, matches against your preferences, prints the report, saves it to a file, and emails it to you.

## External Contributors & AI Tools

- **BeautifulSoup** web scraping approach informed by the [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- **Gmail SMTP** setup based on [Google's App Passwords documentation](https://support.google.com/accounts/answer/185833)
- **Claude Code (Anthropic)** was used as a generative AI tool during development:
  - Claude helped write the initial structure of the `scrape_menu()` function for parsing FoodPro HTML.
  - Claude helped with re-organizing code into separate modules
  - All code was reviewed, tested, and modified by Tracy Yuan.
