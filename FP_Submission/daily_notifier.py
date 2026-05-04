"""
Daily HUDS Menu Notifier (Integrated Pipeline)
CS32 Final Project
Tracy Yuan

Ties together all three modules:
  1. scrape_menu.py    -- scrape website + match preferences
  2. format_report.py  -- format results into readable text
  3. send_email.py     -- send the report via Gmail

Usage:
    python3 daily_notifier.py              # interactive: pick a dining hall
    python3 daily_notifier.py --hall 3     # non-interactive (for cron jobs)
"""

import sys
import os
from datetime import datetime

from scrape_menu import scrape_menu, load_preferences, find_matches, DINING_OPTIONS
from format_report import format_plain_body, format_html_body
from send_email import send_email


def prompt_dining_hall():
    """Prompt the user to select which dining hall to check."""
    print("\nWhich dining hall would you like to check?")
    for num, info in DINING_OPTIONS.items():
        print(f"  {num}. {info['name']}")

    while True:
        choice = input("\nEnter 1, 2, or 3: ").strip()
        if choice in ("1", "2", "3"):
            selected = DINING_OPTIONS[int(choice)]
            print(f"\n  Selected: {selected['name']}\n")
            return selected
        print("  Invalid choice. Please enter 1, 2, or 3.")


def run_pipeline(hall_choice=None):
    """Run the full scrape -> match -> format -> email pipeline.

    Args:
        hall_choice: int (1, 2, or 3) to skip interactive prompt, or None to prompt
    """
    today = datetime.now()
    print(f"\nHUDS Daily Notifier -- {today.strftime('%A, %B %d, %Y')}")
    print("=" * 50)

    # Load preferences
    prefs_path = os.path.join(os.path.dirname(__file__), 'preferences.json')
    prefs = load_preferences(prefs_path)
    print(f"\nPreferences loaded: {len(prefs.get('liked_foods', []))} likes, "
          f"{len(prefs.get('disliked_foods', []))} dislikes")

    excluded = prefs.get("excluded_categories", [])
    if excluded:
        print(f"Excluded categories: {', '.join(excluded)}")

    # Select dining hall
    if hall_choice and hall_choice in DINING_OPTIONS:
        selected = DINING_OPTIONS[hall_choice]
        print(f"Dining hall: {selected['name']}")
    else:
        selected = prompt_dining_hall()

    hall_name = selected["name"]
    location_num = selected["location_num"]

    # Step 1: Scrape
    print("\n[1/3] Scraping menu...")
    menu = scrape_menu(location_num, hall_name, today)

    if not menu:
        print(f"  No menu data found for {hall_name} today.")
        return

    # Step 2: Match
    print("[2/3] Matching against preferences...")
    matches = find_matches(menu, prefs)
    print(f"  Found {len(matches)} matches")

    # Step 3: Format and deliver
    print("[3/3] Formatting report...")

    # Print plain-text version to terminal
    plain_body = format_plain_body(hall_name, matches, today)
    print(f"\n{plain_body}")

    # Save plain-text report to file
    output_file = f"menu_report_{today.strftime('%Y-%m-%d')}.txt"
    with open(output_file, "w") as f:
        f.write(plain_body)
    print(f"Report saved to {output_file}")

    # Send HTML-formatted email
    print("\nSending email...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    html_body = format_html_body(hall_name, matches, today)
    subject = f"HUDS Menu: {len(matches)} matches at {hall_name} -- {today.strftime('%b %d')}"
    send_email(subject, html_body, env_path, html=True)


def main():
    hall_choice = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--hall" and i + 1 < len(args):
            hall_choice = int(args[i + 1])
            i += 2
        else:
            print(f"Unknown argument: {args[i]}")
            print("Usage: python3 daily_notifier.py [--hall 1|2|3]")
            sys.exit(1)

    run_pipeline(hall_choice=hall_choice)


if __name__ == "__main__":
    main()
