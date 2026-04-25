"""
Daily HUDS Menu Notifier (Integrated Pipeline)
CS32 Final Project
Tracy Yuan

Ties together all three modules:
  1. scrape_menu.py    -- scrape website + match preferences
  2. format_report.py  -- format results into readable text
  3. send_email.py     -- send the report via Gmail
"""

import sys
import os
from datetime import datetime

# Add FP_Design to path so we can import modules from there
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'FP_Design'))

from scrape_menu import scrape_menu, load_preferences, find_matches, DINING_OPTIONS
from format_report import format_email_body
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


def run_pipeline():
    """Run the full scrape -> match -> format -> email pipeline."""
    today = datetime.now()
    print(f"\nHUDS Daily Notifier -- {today.strftime('%A, %B %d, %Y')}")
    print("=" * 50)

    # Load preferences
    prefs_path = os.path.join(os.path.dirname(__file__), '..', 'FP_Design', 'preferences.json')
    prefs = load_preferences(prefs_path)
    print(f"\nPreferences loaded: {len(prefs.get('liked_foods', []))} likes, "
          f"{len(prefs.get('disliked_foods', []))} dislikes")

    # Select dining hall
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

    body = format_email_body(hall_name, matches, today)
    print(f"\n{body}")

    # Save to file
    output_file = f"menu_report_{today.strftime('%Y-%m-%d')}.txt"
    with open(output_file, "w") as f:
        f.write(body)
    print(f"Report saved to {output_file}")

    # Email
    print("\nSending email...")
    env_path = os.path.join(os.path.dirname(__file__), '..', 'FP_Design', '.env')
    subject = f"HUDS Menu: {len(matches)} matches at {hall_name} -- {today.strftime('%b %d')}"
    send_email(subject, body, env_path)


def main():
    run_pipeline()


if __name__ == "__main__":
    main()
