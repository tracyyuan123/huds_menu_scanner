"""
Report Formatter
CS32 Final Project
Tracy Yuan

Provides format_email_body, which turns matched menu items into a
nicely formatted plain-text email body with greeting, counts, and sections.
"""

MEALS = ["Breakfast", "Lunch", "Dinner"]


def format_email_body(hall_name, matches, date):
    """Build a formatted plain-text email body from matched items."""

    lines = []
    lines.append(f"Good morning! Here's your personalized HUDS menu for today.\n")
    lines.append(f"  Dining Hall: {hall_name}")
    lines.append(f"  Date: {date.strftime('%A, %B %d, %Y')}")
    lines.append(f"  Total matches: {len(matches)}")
    lines.append("")

    if not matches:
        lines.append("No preference matches found today. Maybe try a different hall?")
        return "\n".join(lines)

    # Group matches by meal
    by_meal = {}
    for m in matches:
        by_meal.setdefault(m["meal"], []).append(m)

    for meal in MEALS:
        meal_matches = by_meal.get(meal, [])
        if not meal_matches:
            continue

        lines.append(f"--- {meal} ({len(meal_matches)} matches) ---")
        for m in meal_matches:
            lines.append(f"  * {m['item']}")
            lines.append(f"    (matched your preference: \"{m['matched_keyword']}\")")
        lines.append("")

    lines.append("Enjoy your meals today!")

    return "\n".join(lines)
