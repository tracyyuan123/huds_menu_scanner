# Dining Hall Menu Scanner & Email Notifier

**CS32 Final Project by Tracy Yuan**

A tool that scrapes the Harvard University Dining Services (HUDS) menu each day, matches menu items against personal food preferences, and emails a personalized HTML report of what to eat.

## What It Does

1. **Scrapes** the daily HUDS dining hall menu from the FoodPro website using `requests` and `BeautifulSoup`
2. **Matches** menu items against a configurable list of liked/disliked foods using substring matching with a fuzzy matching fallback (`thefuzz` library)
3. **Filters** out excluded categories (e.g., "Salad Bar") and deduplicates items across categories
4. **Formats** a plain-text summary for the terminal and an HTML-formatted email
5. **Emails** the HTML report to your inbox via Gmail SMTP
6. **Saves** a local copy of the report as a `.txt` file

## Project Files

| File | Location | Purpose |
|------|----------|---------|
| `scrape_menu.py` | `FP_Submission/` | Library module: scrapes FoodPro website, matches items with fuzzy matching, filters categories |
| `format_report.py` | `FP_Submission/` | Formats matched results into plain text (terminal) and HTML (email) |
| `send_email.py` | `FP_Submission/` | Sends emails via Gmail SMTP (supports plain text and HTML) |
| `daily_notifier.py` | `FP_Submission/` | Pipeline orchestrator: imports from the three modules above |
| `preferences.json` | `FP_Submission/` | User food preferences config (liked foods, disliked foods, excluded categories) |
| `.env` | `FP_Submission/` | Gmail credentials (not committed -- see setup below) |
| `changes.md` | `FP_Submission/` | Changelog documenting all changes from FP_Status to FP_Submission |

## Setup

### 1. Install dependencies

```
pip install requests beautifulsoup4 thefuzz
```

### 2. Configure food preferences

Edit `FP_Submission/preferences.json` with your own liked and disliked foods and categories to exclude:

```json
{
    "liked_foods": ["chicken", "salmon", "rice", "pasta", "cake"],
    "disliked_foods": ["cheese", "beets", "liver"],
    "excluded_categories": ["Salad Bar", "From the Grill"]
}
```

- **liked_foods**: keywords to match against menu items (substring + fuzzy matching)
- **disliked_foods**: keywords that override likes (e.g., "cheese" excludes "New York Cheese Cake" even though "cake" is liked)
- **excluded_categories**: menu categories to skip entirely (e.g., daily-repeat items)

### 3. Set up email credentials

1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Create an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Copy `.env.example` to `.env` and fill in your credentials:

```
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
NOTIFY_EMAIL=your_email@gmail.com
```

## How to Run

### Interactive mode

From the `FP_Submission/` directory:

```
python3 daily_notifier.py
```

The script will prompt you to pick a dining hall:
1. Annenberg
2. Quincy House
3. House (except Quincy)

### Non-interactive mode (for cron jobs)

```
python3 daily_notifier.py --hall 3
```

The `--hall` flag skips the interactive prompt, making it compatible with scheduled automation.

### Setting up a cron job (macOS)

A cron job is a macOS/Linux system feature that runs a command on a schedule -- it's configured on your laptop, not in the Python code. To set one up:

1. Open Terminal and run:
   ```
   crontab -e
   ```
   This opens your cron schedule in a text editor (usually vim -- press `i` to enter insert mode).

2. Add a line like this (adjust the paths to match your setup):
   ```
   0 7 * * * cd /path/to/FP_Submission && /path/to/python3 daily_notifier.py --hall 3
   ```
   The format is `minute hour day month weekday command`. So `0 7 * * *` means "at 7:00 AM every day."

   **Important:** Use the full path to your python3 binary, not just `python3`. Cron runs in a minimal environment without your shell's PATH. Run `which python3` in Terminal to find the correct path (e.g., if you use anaconda, it will be something like `/Users/you/opt/anaconda3/bin/python3`).

3. Save and exit (in vim: press `Esc`, then type `:wq` and press Enter).

4. macOS requires you to grant **Full Disk Access** to `/usr/sbin/cron` for cron jobs to run. Go to **System Settings > Privacy & Security > Full Disk Access**, click `+`, and add `/usr/sbin/cron`.

To view your current cron jobs: `crontab -l`
To remove all cron jobs: `crontab -r`

## External Contributors & AI Tools

- **BeautifulSoup** web scraping approach informed by the [Beautiful Soup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- **Gmail SMTP** setup based on [Google's App Passwords documentation](https://support.google.com/accounts/answer/185833)
- **thefuzz** fuzzy string matching based on the [thefuzz library documentation](https://github.com/seatgeek/thefuzz)
- **Claude Code (Anthropic)** was used as a generative AI tool during development:
  - Claude helped write the initial structure of the `scrape_menu()` function for parsing FoodPro HTML
  - Claude helped with re-organizing code into separate modules
  - Claude helped write docstring for functions
  - Claude helped implement HTML email formatting
  - All code was reviewed, tested, and modified by Tracy Yuan
