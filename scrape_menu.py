"""
HUDS Dining Hall Menu Scraper & Preference Matcher
CS32 Final Project -- Tracy Yuan

Scrapes the Harvard University Dining Services (HUDS) daily menu from the
FoodPro website, matches items against user preferences loaded from a JSON
config file, and outputs a personalized meal summary.

New skill learned: web scraping with BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_URL = "https://www.foodpro.huds.harvard.edu/foodpro/shtmenu.aspx"

# Dining hall options matching the HUDS website
# See: https://www.dining.harvard.edu/weeks-undergraduate-menus
DINING_OPTIONS = {
    1: {"name": "Annenberg",             "location_num": 30},
    2: {"name": "Quincy House",          "location_num":  8},
    3: {"name": "House (except Quincy)", "location_num": 38},
}

MEALS = ["Breakfast", "Lunch", "Dinner"]


# ---------------------------------------------------------------------------
# 1. Fetch and parse the daily menu
# ---------------------------------------------------------------------------

# Example URL: https://www.foodpro.huds.harvard.edu/foodpro/shtmenu.aspx?sName=HARVARD+UNIVERSITY+DINING+SERVICES&locationNum=38&locationName=Dining+Hall&naFlag=1&WeeksMenus=This+Week%27s+Menus&myaction=read&dtdate=4%2f7%2f2026

def build_menu_url(location_num, location_name, date):
    """Build the FoodPro short-menu URL for a given hall and date."""
    date_str = date.strftime("%-m/%-d/%Y")  # e.g. "4/7/2026"
    params = {
        "sName": "HARVARD UNIVERSITY DINING SERVICES",
        "locationNum": f"{location_num:02d}",
        "locationName": location_name,
        "naFlag": "1",
        "WeeksMenus": "This Week's Menus",
        "myaction": "read",
        "dtdate": date_str,
    }
    req = requests.Request("GET", BASE_URL, params=params)
    prepared = req.prepare()
    return prepared.url


def scrape_menu(location_num, location_name, date):
    """Scrape the short-menu page for one dining hall on one date.

    Returns a dict: meal -> category -> [item names]
    e.g. {"Lunch": {"Entrees": ["Grilled Chicken", ...], ...}, ...}
    """
    url = build_menu_url(location_num, location_name, date)
    print(f"  Fetching {location_name} menu for {date.strftime('%A, %B %d')}...")
    print(f"  URL: {url}\n")

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    menu = {}

    # The page has one main table; each top-level <td> is a meal column
    main_table = soup.find("table", attrs={"width": "100%", "align": "center"})
    if not main_table:
        print(f"  WARNING: could not find main table for {location_name}")
        return menu

    meal_cells = main_table.find("tr").find_all("td", recursive=False)

    for cell in meal_cells:
        # Determine the meal name from the link text (e.g. "Breakfast Menu")
        link = cell.find("a")
        if not link:
            continue
        meal_text = link.get_text(strip=True)
        meal_name = meal_text.replace(" Menu", "").strip()

        # Parse categories and items within this cell
        meal_data = {}
        current_category = "Other"

        inner_table = cell.find("table")
        if not inner_table:
            continue

        for row in inner_table.find_all("tr"):
            cat_div = row.find("div", class_="shortmenucats")
            item_div = row.find("div", class_="shortmenurecipes")

            if cat_div:
                raw = cat_div.get_text(strip=True)
                current_category = raw.strip("-").strip()
            elif item_div:
                item_name = item_div.get_text(strip=True)
                if item_name:
                    # The FoodPro HTML duplicates each item; skip if already seen
                    cat_list = meal_data.setdefault(current_category, [])
                    if item_name not in cat_list:
                        cat_list.append(item_name)

        if meal_data:
            menu[meal_name] = meal_data

    return menu


# ---------------------------------------------------------------------------
# 2. Match each item against user preferences
# ---------------------------------------------------------------------------

def load_preferences(filepath="preferences.json"):
    """Load user preferences from a JSON file."""
    with open(filepath) as f:
        return json.load(f)


def match_item(item_name, preferences):
    """Check whether a menu item matches any liked-food keyword.

    Uses case-insensitive substring matching.  For example, a preference
    for "chicken" will match "Grilled Chicken Breast" and "Chicken Tikka".

    Returns the matching keyword string if found, or None.
    """
    item_lower = item_name.lower()

    # First check dislikes -- if it matches a dislike, skip it
    for dislike in preferences.get("disliked_foods", []):
        if dislike.lower() in item_lower:
            return None

    # Then check likes
    for keyword in preferences.get("liked_foods", []):
        if keyword.lower() in item_lower:
            return keyword

    return None


def find_matches(menu, preferences):
    """Scan an entire dining-hall menu and return matched items.

    Returns a list of dicts with keys: meal, category, item, matched_keyword
    """
    matches = []
    for meal, categories in menu.items():
        for category, items in categories.items():
            for item in items:
                keyword = match_item(item, preferences)
                if keyword:
                    matches.append({
                        "meal": meal,
                        "category": category,
                        "item": item,
                        "matched_keyword": keyword,
                    })
    return matches


# ---------------------------------------------------------------------------
# 3. Format and save results
# ---------------------------------------------------------------------------

def format_summary(hall_name, matches, date):
    """Create a human-readable summary of matched menu items."""
    lines = []
    lines.append(f"=== {hall_name} -- {date.strftime('%A, %B %d, %Y')} ===\n")

    if not matches:
        lines.append("  No preference matches found today.\n")
        return "\n".join(lines)

    # Group matches by meal
    by_meal = {}
    for m in matches:
        by_meal.setdefault(m["meal"], []).append(m)

    for meal in MEALS:
        meal_matches = by_meal.get(meal, [])
        if not meal_matches:
            continue
        lines.append(f"  {meal}:")
        for m in meal_matches:
            lines.append(f"    - {m['item']}  (matched: \"{m['matched_keyword']}\")")
        lines.append("")

    return "\n".join(lines)


def print_full_menu(hall_name, menu):
    """Print every item scraped from a dining hall."""
    print(f"\n--- Full menu for {hall_name} ---")
    for meal, categories in menu.items():
        print(f"\n  {meal}:")
        for category, items in categories.items():
            print(f"    [{category}]")
            for item in items:
                print(f"      - {item}")
    print()


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

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


def main():
    today = datetime.now()
    print(f"HUDS Menu Scanner -- {today.strftime('%A, %B %d, %Y')}")
    print("=" * 50)

    # Load preferences
    prefs = load_preferences()
    print(f"\nLoaded {len(prefs['liked_foods'])} liked-food keywords from preferences.json")
    print(f"Liked: {', '.join(prefs['liked_foods'][:5])}...")

    # Ask the user which dining hall to check
    selected = prompt_dining_hall()
    hall_name = selected["name"]
    location_num = selected["location_num"]

    # --- Step 1: Scrape the menu ---
    menu = scrape_menu(location_num, hall_name, today)

    if not menu:
        print(f"  No menu data found for {hall_name} today.")
        return

    print_full_menu(hall_name, menu)

    # --- Step 2: Match against preferences ---
    matches = find_matches(menu, prefs)
    summary = format_summary(hall_name, matches, today)
    print(summary)

    # --- Step 3: Save report to file ---
    output_file = f"menu_report_{today.strftime('%Y-%m-%d')}.txt"
    with open(output_file, "w") as f:
        f.write(f"HUDS Menu Report -- {today.strftime('%A, %B %d, %Y')}\n\n")
        f.write(summary)
    print(f"Report saved to {output_file}")


if __name__ == "__main__":
    main()
