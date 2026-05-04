"""
Menu Scraper & Preference Matcher (library module)
CS32 Final Project
Tracy Yuan

Scrapes the Harvard University Dining Services (HUDS) daily menu from the
FoodPro website and matches items against user preferences loaded from a
JSON config file. Imported by daily_notifier.py.
"""

import requests
from bs4 import BeautifulSoup
import json
from thefuzz import fuzz

# –––– Menu Scraper ––––

BASE_URL = "https://www.foodpro.huds.harvard.edu/foodpro/shtmenu.aspx"

# Dining hall options matching the HUDS website
# See: https://www.dining.harvard.edu/weeks-undergraduate-menus
DINING_OPTIONS = {
    1: {"name": "Annenberg",             "location_num": 30},
    2: {"name": "Quincy House",          "location_num":  8},
    3: {"name": "House (except Quincy)", "location_num": 38},
}

MEALS = ["Breakfast", "Lunch", "Dinner"]

# Fuzzy matching threshold (0-100). Scores above this count as a match.
FUZZY_THRESHOLD = 90

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
    meal_cells = main_table.find("tr").find_all("td", recursive=False)

    for cell in meal_cells:  # loop through each meal column (Breakfast, Lunch, Dinner)
        link = cell.find("a")
        if not link:
            continue
        meal_text = link.get_text(strip=True)       # e.g. "Breakfast Menu"
        meal_name = meal_text.replace(" Menu", "").strip()  # e.g. "Breakfast"

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
                    # FoodPro HTML duplicates each item; skip if already seen in this category
                    cat_list = meal_data.setdefault(current_category, [])
                    if item_name not in cat_list:
                        cat_list.append(item_name)

        if meal_data:
            menu[meal_name] = meal_data

    return menu


# –––– Preference Matcher ––––

def load_preferences(filepath="preferences.json"):
    """Load user preferences from a JSON file."""
    with open(filepath) as f:
        return json.load(f)


def match_item(item_name, preferences):
    """Check whether a menu item matches any liked-food keyword.

    First tries exact substring matching (fast). If no substring match is
    found, falls back to fuzzy matching using thefuzz library.

    Returns the matching keyword string if found, or None.
    """
    item_lower = item_name.lower()

    # First check dislikes -- dislikes always override likes
    for dislike in preferences.get("disliked_foods", []):
        if dislike.lower() in item_lower:
            return None

    # Try exact substring matching first (fast path)
    for keyword in preferences.get("liked_foods", []):
        if keyword.lower() in item_lower:
            return keyword

    # Fuzzy matching fallback: check if any keyword is a close match
    for keyword in preferences.get("liked_foods", []):
        score = fuzz.partial_ratio(keyword.lower(), item_lower)
        if score >= FUZZY_THRESHOLD:
            return keyword  # fuzzy match found

    return None


def find_matches(menu, preferences):
    """Scan an entire dining-hall menu and return matched items.

    Skips categories listed in preferences["excluded_categories"].
    Deduplicates items that appear under multiple categories in the same meal.

    Returns a list of dicts with keys: meal, category, item, matched_keyword
    """
    excluded = [c.lower() for c in preferences.get("excluded_categories", [])]
    matches = []

    for meal, categories in menu.items():
        seen_items = set()  # track item names already matched in this meal

        for category, items in categories.items():
            # Skip excluded categories (e.g. "Salad Bar", "From the Grill")
            if category.lower() in excluded:
                continue

            for item in items:
                # Skip if this item was already matched in a different category
                if item in seen_items:
                    continue

                keyword = match_item(item, preferences)
                if keyword:
                    matches.append({
                        "meal": meal,
                        "category": category,
                        "item": item,
                        "matched_keyword": keyword,
                    })
                    seen_items.add(item)

    return matches
