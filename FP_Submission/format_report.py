"""
Report Formatter
CS32 Final Project
Tracy Yuan

Provides two formatting functions:
  - format_plain_body: plain-text version for terminal output
  - format_html_body:  HTML version for email delivery
"""

MEALS = ["Breakfast", "Lunch", "Dinner"]


def format_plain_body(hall_name, matches, date):
    """Build a plain-text report for terminal display."""

    lines = []
    lines.append(f"=== {hall_name} -- {date.strftime('%A, %B %d, %Y')} ===")
    lines.append(f"Total matches: {len(matches)}\n")

    if not matches:
        lines.append("No preference matches found today.")
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


def format_html_body(hall_name, matches, date):
    """Build an HTML email body from matched items.

    Uses bold meal headers, bulleted items, and a summary at the top.
    """

    lines = []
    lines.append("<html><body>")
    lines.append(f"<p>Good morning! Here's your personalized HUDS menu for today.</p>")
    lines.append(f"<p><b>Dining Hall:</b> {hall_name}<br>")
    lines.append(f"<b>Date:</b> {date.strftime('%A, %B %d, %Y')}<br>")
    lines.append(f"<b>Total matches:</b> {len(matches)}</p>")

    if not matches:
        lines.append("<p>No preference matches found today. Maybe try a different hall?</p>")
        lines.append("</body></html>")
        return "\n".join(lines)

    # Group matches by meal
    by_meal = {}
    for m in matches:
        by_meal.setdefault(m["meal"], []).append(m)

    for meal in MEALS:
        meal_matches = by_meal.get(meal, [])
        if not meal_matches:
            continue

        lines.append(f"<h3>{meal} ({len(meal_matches)} matches)</h3>")
        lines.append("<ul>")
        for m in meal_matches:
            lines.append(f"  <li><b>{m['item']}</b> "
                         f"<i>(matched: \"{m['matched_keyword']}\")</i></li>")
        lines.append("</ul>")

    lines.append("<p>Enjoy your meals today!</p>")
    lines.append("</body></html>")

    return "\n".join(lines)
