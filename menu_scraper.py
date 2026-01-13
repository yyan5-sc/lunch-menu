#!/usr/bin/env python3
"""
Snap Palo Alto Cafeteria Menu Scraper & Slack Notifier

This script scrapes the weekly menu from the Bon Appétit cafeteria website
and sends a formatted message to a Slack channel.

Usage:
    python menu_scraper.py
    
Environment Variables:
    SLACK_WEBHOOK_URL: Slack Incoming Webhook URL (required)
    CAFE_LOCATION: Cafeteria location (default: palo-alto)
"""

import os
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re


# Configuration
CAFE_LOCATIONS = {
    "palo-alto": "snap-palo-alto",
    "santa-monica": "snap-santa-monica",
    "seattle": "snap-seattle",
    "san-francisco": "snap-san-francisco",
    "bellevue": "snap-bellevue",
    "new-york": "snap-new-york",
}

BASE_URL = "https://{location}.cafebonappetit.com/cafe/{date}/"

# Keywords for categorizing menu items
MEAT_KEYWORDS = [
    'beef', 'steak', 'pork', 'bacon', 'ham', 'sausage', 'lamb', 'veal',
    'chicken', 'turkey', 'duck', 'poultry', 'wing', 'thigh', 'breast',
    'ribs', 'brisket', 'meatball', 'burger', 'patty', 'pulled pork',
    'braised beef', 'carnitas', 'chorizo', 'prosciutto', 'pepperoni',
    'teriyaki chicken', 'fried chicken', 'bbq chicken', 'rotisserie',
    'bulgogi', 'galbi', 'kalbi', 'korean bbq', 'bibimbap', 'japchae',
    'dakgalbi', 'samgyeopsal', 'bo ssam', 'bossam', 'katsu', 'tonkatsu',
    'karaage', 'gyudon', 'yakitori', 'donburi', 'yakiniku', 'ribeye',
    'chashu', 'nikujaga', 'char siu', 'mapo', 'kung pao', 'orange chicken',
    'general tso', 'mongolian beef', 'szechuan', 'sichuan', 'satay', 'rendang',
    'adobo', 'larb', 'laab'
]

SEAFOOD_KEYWORDS = [
    'fish', 'salmon', 'tuna', 'cod', 'tilapia', 'halibut', 'mahi', 'trout',
    'shrimp', 'prawn', 'lobster', 'crab', 'clam', 'mussel', 'oyster', 
    'scallop', 'squid', 'calamari', 'octopus', 'seafood', 'sushi', 'sashimi',
    'poke', 'ceviche', 'anchovy', 'sardine', 'bass', 'snapper', 'ahi',
    'unagi', 'eel', 'ikura', 'ebi', 'hotate', 'uni'
]

# Non-food items to exclude
EXCLUDE_KEYWORDS = [
    'nutrition', 'ingredients', 'read more', 'cal.', 'calories',
    'menu icon', 'legend', 'subscribe', 'email', 'contact',
    'hours', 'served from', 'closed', 'copyright', 'privacy',
    'terms of use', 'secondary navigation', 'primary navigation',
    'stay fresh', 'the power of', 'the buzz', 'wellness',
    'sustainability', 'food allergies', 'hide descriptions',
    'collapse dayparts', 'menu mail', 'tell us', 'faq',
    'icons', 'about your food', 'snapchat', 'days', 'café', 'cafe',
    'filters', 'show', 'exclude', 'clear filters', 'apply filters',
    'view menu', 'palo alto', 'santa monica', 'seattle', 'new york',
    'san francisco', 'bellevue', 'friday', 'monday', 'tuesday',
    'wednesday', 'thursday', 'tomorrow', 'today', 'breakfast',
    'coffee bar', 'condiments', 'extras', 'specials', 'station',
    'may contain', 'gluten', 'vegan:', 'vegetarian:', 'dairy',
    'allergen', 'kitchen', 'prepared in', 'raw/undercooked',
    'copyright', 'bon appétit', 'bon appetit',
    # Article/blog titles
    'eat with your senses', 'improve your mood', 'upcycle your',
    'boards, boards', 'how to plan', 'simple shifts', 'beat holiday',
    'ways to uplift', 'gift (guide)', 'gift guide', 'power of mental',
    'tree nut', 'ask us', 'am -', 'pm -', '- pm', '- am',
    # More UI elements
    'light breakfast', 'desserts'
]

# Main dish stations (these are the featured items we want to highlight)
MAIN_DISH_STATIONS = [
    'the daily dish', 'daily dish', 'grill', 'wok', 'exhibition',
    'chef', 'entree', 'hot food', 'global', 'comfort', 'green lite'
]

# Stations to EXCLUDE from meat/seafood highlights (sides, beverages, etc.)
EXCLUDE_STATIONS = [
    'bowl bar enhancements', 'beverages', 'coffee bar',
    'soup', 'desserts', 'condiments'
]

# Specific items to exclude (always-available salad bar items, NOT main dishes)
EXCLUDE_ITEMS = [
    'tuna salad',  # This is a salad bar topping, not a main dish
    'parmesan cheese', 'shredded cheese', 'croutons',
    'cage free egg',  # Salad bar topping
]


def get_week_dates(start_date: Optional[datetime] = None) -> List[str]:
    """
    Get dates for Monday through Friday of the current week.
    
    Args:
        start_date: Starting date (default: today)
    
    Returns:
        List of date strings in YYYY-MM-DD format
    """
    if start_date is None:
        start_date = datetime.now()
    
    # Find Monday of this week
    days_since_monday = start_date.weekday()
    monday = start_date - timedelta(days=days_since_monday)
    
    # Generate Monday to Friday
    dates = []
    for i in range(5):  # Mon=0, Tue=1, Wed=2, Thu=3, Fri=4
        date = monday + timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    
    return dates


def is_valid_menu_item(text: str) -> bool:
    """Check if text is a valid menu item name."""
    text_lower = text.lower().strip()
    
    # Too short or too long
    if len(text) < 4 or len(text) > 60:
        return False
    
    # Contains excluded keywords
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in text_lower:
            return False
    
    # Is just a number or calorie info
    if re.match(r'^\d+\s*(cal\.?|calories?)?\s*$', text_lower):
        return False
    
    # Skip single words that are likely not menu items
    if len(text.split()) == 1 and len(text) < 10:
        # But allow some known food words
        known_foods = ['oatmeal', 'congee', 'pasta', 'rice', 'soup', 'salad']
        if text_lower not in known_foods:
            return False
    
    # Skip items that are just dietary labels
    if text_lower in ['vegan', 'vegetarian', 'gluten-free', 'organic']:
        return False
    
    # Skip navigation/UI elements
    if any(x in text_lower for x in ['click', 'select', 'choose', 'option']):
        return False
    
    return True


def categorize_item(item_name: str) -> str:
    """
    Categorize a menu item as meat, seafood, or other.
    
    Returns: 'meat', 'seafood', or 'other'
    """
    item_lower = item_name.lower()
    
    # Check for seafood first (more specific)
    for keyword in SEAFOOD_KEYWORDS:
        if keyword in item_lower:
            return 'seafood'
    
    # Check for meat
    for keyword in MEAT_KEYWORDS:
        if keyword in item_lower:
            return 'meat'
    
    return 'other'


def scrape_menu_for_date(location: str, date: str) -> Dict:
    """
    Scrape the LUNCH menu for a specific date.
    
    Args:
        location: Cafe location key
        date: Date in YYYY-MM-DD format
    
    Returns:
        Dictionary with categorized menu information (meat/seafood highlighted)
    """
    location_subdomain = CAFE_LOCATIONS.get(location, location)
    url = BASE_URL.format(location=location_subdomain, date=date)
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        menu_data = {
            "date": date,
            "url": url,
            "meat": [],
            "seafood": [],
            "other": [],
            "stations": {}
        }
        
        # Find the Lunch section container by ID
        lunch_container = soup.find(id=lambda x: x and 'lunch' in x.lower() if x else False)
        
        if not lunch_container:
            # Fallback: try to find by section header
            lunch_header = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'lunch' in tag.get_text().lower())
            if lunch_header:
                lunch_container = lunch_header.find_parent('section') or lunch_header.find_parent('div')
        
        if not lunch_container:
            print(f"  Warning: Could not find lunch section for {date}")
            return menu_data
        
        # Find all menu items within the lunch section
        items = lunch_container.find_all(class_='site-panel__daypart-item')
        seen_items = set()
        
        for item in items:
            # Get item title
            title_elem = item.find(class_='site-panel__daypart-item-title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            
            # Skip invalid items
            if not title or not is_valid_menu_item(title):
                continue
            
            # Skip specific excluded items (like "Tuna Salad" which is a salad bar item)
            if title.lower() in [x.lower() for x in EXCLUDE_ITEMS]:
                continue
            
            # Skip duplicates
            if title in seen_items:
                continue
            seen_items.add(title)
            
            # Get station name
            station_elem = item.find(class_='site-panel__daypart-item-station')
            station = station_elem.get_text(strip=True).lstrip('@') if station_elem else "General"
            station_lower = station.lower()
            
            # Check if this is from an excluded station (salad bar, beverages, etc.)
            is_excluded_station = any(excl in station_lower for excl in EXCLUDE_STATIONS)
            
            # Check if this is from a main dish station
            is_main_dish_station = any(main in station_lower for main in MAIN_DISH_STATIONS)
            
            # Add to station list
            if station not in menu_data["stations"]:
                menu_data["stations"][station] = []
            menu_data["stations"][station].append(title)
            
            # Only categorize as meat/seafood if from main dish station (not salad bar)
            category = categorize_item(title)
            
            if category in ['meat', 'seafood']:
                # Only add to meat/seafood if it's from a main dish station
                if is_main_dish_station and not is_excluded_station:
                    menu_data[category].append(title)
                else:
                    # It's meat/seafood but from salad bar - add to other
                    menu_data['other'].append(title)
            else:
                menu_data['other'].append(title)
        
        # Deduplicate lists
        menu_data["meat"] = list(dict.fromkeys(menu_data["meat"]))
        menu_data["seafood"] = list(dict.fromkeys(menu_data["seafood"]))
        menu_data["other"] = list(dict.fromkeys(menu_data["other"]))
        
        return menu_data
        
    except requests.RequestException as e:
        print(f"Error fetching menu for {date}: {e}")
        return {
            "date": date,
            "url": url,
            "error": str(e),
            "meat": [],
            "seafood": [],
            "other": [],
            "stations": {}
        }


def scrape_weekly_menu(location: str = "palo-alto") -> List[Dict]:
    """
    Scrape the menu for the entire week.
    
    Args:
        location: Cafe location key
    
    Returns:
        List of daily menu dictionaries
    """
    dates = get_week_dates()
    weekly_menu = []
    
    for date in dates:
        print(f"Scraping menu for {date}...")
        menu = scrape_menu_for_date(location, date)
        weekly_menu.append(menu)
    
    return weekly_menu


def format_slack_message(weekly_menu: List[Dict], location: str = "palo-alto") -> Dict:
    """
    Format the weekly lunch menu into a Slack message with blocks.
    Meat and seafood are highlighted at the top.
    
    Args:
        weekly_menu: List of daily menu dictionaries
        location: Cafe location name
    
    Returns:
        Slack message payload
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🍽️ {location.replace('-', ' ').title()} - Weekly Lunch Menu",
                "emoji": True
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"📅 Week of {weekly_menu[0]['date']} to {weekly_menu[-1]['date']}"
                }
            ]
        },
        {"type": "divider"}
    ]
    
    for i, menu in enumerate(weekly_menu):
        date_obj = datetime.strptime(menu['date'], '%Y-%m-%d')
        date_display = date_obj.strftime('%m/%d')
        
        # Day header
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{day_names[i]} - {date_display}*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "View Menu 🔗",
                    "emoji": True
                },
                "url": menu['url'],
                "action_id": f"view_menu_{i}"
            }
        })
        
        if menu.get('error'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ Could not fetch menu: {menu['error']}"
                }
            })
        else:
            menu_text_parts = []
            
            # Meat first (highlighted)
            if menu.get('meat'):
                meat_preview = menu['meat'][:6]
                meat_str = " • ".join(meat_preview)
                if len(menu['meat']) > 6:
                    meat_str += f" _(+{len(menu['meat']) - 6})_"
                menu_text_parts.append(f"🥩 *Meat*: {meat_str}")
            
            # Seafood second (highlighted)
            if menu.get('seafood'):
                seafood_preview = menu['seafood'][:4]
                seafood_str = " • ".join(seafood_preview)
                if len(menu['seafood']) > 4:
                    seafood_str += f" _(+{len(menu['seafood']) - 4})_"
                menu_text_parts.append(f"🐟 *Seafood*: {seafood_str}")
            
            # Other (condensed)
            if menu.get('other'):
                other_preview = menu['other'][:4]
                other_str = ", ".join(other_preview)
                if len(menu['other']) > 4:
                    other_str += f" _(+{len(menu['other']) - 4})_"
                menu_text_parts.append(f"🥗 *Other*: {other_str}")
            
            if menu_text_parts:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "\n".join(menu_text_parts)
                    }
                })
        
        blocks.append({"type": "divider"})
    
    # Footer
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "🤖 Auto-generated by Cafe Menu Bot | Lunch only | 🥩🐟 Highlighted at top"
            }
        ]
    })
    
    return {"blocks": blocks}


def format_simple_slack_message(weekly_menu: List[Dict], location: str = "palo-alto") -> Dict:
    """
    Format a text-based Slack message with meat/seafood highlighted at top.
    
    Args:
        weekly_menu: List of daily menu dictionaries
        location: Cafe location name
    
    Returns:
        Slack message payload
    """
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    lines = [
        f"🍽️ *{location.replace('-', ' ').title()} Cafeteria - Weekly Lunch Menu*",
        f"📅 Week of {weekly_menu[0]['date']} to {weekly_menu[-1]['date']}",
        ""
    ]
    
    for i, menu in enumerate(weekly_menu):
        date_obj = datetime.strptime(menu['date'], '%Y-%m-%d')
        date_display = date_obj.strftime('%m/%d')
        
        lines.append("━" * 35)
        lines.append(f"*{day_names[i]} - {date_display}*")
        lines.append(f"<{menu['url']}|🔗 View Full Menu>")
        
        if menu.get('error'):
            lines.append(f"⚠️ Could not fetch menu: {menu['error']}")
            continue
        
        # Meat dishes first (highlighted)
        if menu.get('meat'):
            meat_items = menu['meat'][:8]  # Limit to 8 items
            lines.append(f"\n🥩 *Meat* ({len(menu['meat'])} items)")
            for item in meat_items:
                lines.append(f"  • {item}")
            if len(menu['meat']) > 8:
                lines.append(f"  _...+{len(menu['meat']) - 8} more_")
        
        # Seafood dishes second (highlighted)
        if menu.get('seafood'):
            seafood_items = menu['seafood'][:5]  # Limit to 5 items
            lines.append(f"\n🐟 *Seafood* ({len(menu['seafood'])} items)")
            for item in seafood_items:
                lines.append(f"  • {item}")
            if len(menu['seafood']) > 5:
                lines.append(f"  _...+{len(menu['seafood']) - 5} more_")
        
        # Other dishes (condensed)
        if menu.get('other'):
            other_items = menu['other'][:5]  # Show only first 5
            lines.append(f"\n🥗 *Other* ({len(menu['other'])} items)")
            lines.append(f"  {', '.join(other_items)}")
            if len(menu['other']) > 5:
                lines.append(f"  _...+{len(menu['other']) - 5} more_")
        
        # Empty line between days
        lines.append("")
    
    lines.append("━" * 35)
    lines.append("🤖 _Auto-generated by Cafe Menu Bot_")
    
    return {"text": "\n".join(lines)}


def send_to_slack(message: Dict, webhook_url: str) -> bool:
    """
    Send message to Slack via webhook.
    
    Args:
        message: Slack message payload
        webhook_url: Slack Incoming Webhook URL
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        print("✅ Message sent to Slack successfully!")
        return True
    except requests.RequestException as e:
        print(f"❌ Failed to send message to Slack: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False


def main():
    """Main entry point."""
    # Get configuration from environment
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    location = os.environ.get("CAFE_LOCATION", "palo-alto")
    
    if not webhook_url:
        print("❌ Error: SLACK_WEBHOOK_URL environment variable is required")
        print("\nTo set up a Slack webhook:")
        print("1. Go to https://api.slack.com/apps")
        print("2. Create a new app or select existing one")
        print("3. Add 'Incoming Webhooks' feature")
        print("4. Create a webhook for your channel")
        print("5. Set SLACK_WEBHOOK_URL environment variable")
        return
    
    print(f"🍽️ Scraping weekly LUNCH menu for {location}...")
    print("   (Meat 🥩 and Seafood 🐟 will be highlighted at top)")
    weekly_menu = scrape_weekly_menu(location)
    
    # Print summary
    for menu in weekly_menu:
        print(f"   {menu['date']}: {len(menu.get('meat', []))} meat, {len(menu.get('seafood', []))} seafood, {len(menu.get('other', []))} other")
    
    print("\n📝 Formatting Slack message...")
    # Use simple format for better compatibility
    message = format_simple_slack_message(weekly_menu, location)
    
    print("\n📤 Sending to Slack...")
    send_to_slack(message, webhook_url)


if __name__ == "__main__":
    main()
