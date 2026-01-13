#!/usr/bin/env python3
"""
Cafe Menu Generator - Creates a beautiful HTML menu file
Opens automatically on your Desktop every Monday
"""

import os
import subprocess
from datetime import datetime
from menu_scraper import scrape_weekly_menu, get_week_dates

# Output locations
OUTPUT_DIR = os.path.expanduser("~/Desktop")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "weekly_lunch_menu.html")

# Shared folder (update this to your team's shared folder if needed)
# Examples: Google Drive, Dropbox, or a network share
SHARED_DIR = os.path.expanduser("~/Desktop")  # Change this to shared folder path
SHARED_FILE = os.path.join(SHARED_DIR, "weekly_lunch_menu.html")


def generate_html(weekly_menu: list, location: str = "palo-alto") -> str:
    """Generate a beautiful HTML page for the weekly menu."""
    
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    # Get week range
    start_date = weekly_menu[0]['date']
    end_date = weekly_menu[-1]['date']
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Lunch Menu - {start_date} to {end_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            color: #1a365d;
            margin-bottom: 40px;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            color: #1a365d;
        }}
        
        header p {{
            font-size: 1.2rem;
            color: #4a5568;
        }}
        
        .generated-time {{
            font-size: 0.9rem;
            color: #718096;
            margin-top: 10px;
        }}
        
        .day-card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .day-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .day-name {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
        }}
        
        .day-date {{
            font-size: 1rem;
            color: #666;
            background: #f5f5f5;
            padding: 6px 12px;
            border-radius: 20px;
        }}
        
        .menu-link {{
            font-size: 0.9rem;
            color: #667eea;
            text-decoration: none;
        }}
        
        .menu-link:hover {{
            text-decoration: underline;
        }}
        
        .category {{
            margin-bottom: 20px;
        }}
        
        .category:last-child {{
            margin-bottom: 0;
        }}
        
        .category-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
        }}
        
        .category-icon {{
            font-size: 1.5rem;
        }}
        
        .category-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
        }}
        
        .category-count {{
            font-size: 0.85rem;
            color: #999;
            background: #f5f5f5;
            padding: 2px 8px;
            border-radius: 10px;
        }}
        
        .meat-section {{
            background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #e74c3c;
        }}
        
        .seafood-section {{
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #3498db;
        }}
        
        .other-section {{
            background: #f9f9f9;
            border-radius: 12px;
            padding: 16px;
            border-left: 4px solid #95a5a6;
        }}
        
        .items-list {{
            list-style: none;
        }}
        
        .items-list li {{
            padding: 6px 0;
            color: #444;
            font-size: 0.95rem;
        }}
        
        .items-list li:before {{
            content: "•";
            color: #999;
            margin-right: 8px;
        }}
        
        .items-inline {{
            color: #666;
            font-size: 0.9rem;
            line-height: 1.6;
        }}
        
        .more-items {{
            color: #999;
            font-style: italic;
            font-size: 0.85rem;
            margin-top: 8px;
        }}
        
        .no-items {{
            color: #999;
            font-style: italic;
        }}
        
        footer {{
            text-align: center;
            color: #718096;
            margin-top: 40px;
            font-size: 0.9rem;
        }}
        
        @media (max-width: 600px) {{
            header h1 {{
                font-size: 1.8rem;
            }}
            .day-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍽️ Weekly Lunch Menu</h1>
            <p>{location.replace('-', ' ').title()} Cafeteria</p>
            <p class="generated-time">Generated: {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}</p>
        </header>
"""
    
    for i, menu in enumerate(weekly_menu):
        date_obj = datetime.strptime(menu['date'], '%Y-%m-%d')
        date_display = date_obj.strftime('%B %d')
        
        html += f"""
        <div class="day-card">
            <div class="day-header">
                <div>
                    <span class="day-name">{day_names[i]}</span>
                    <span class="day-date">{date_display}</span>
                </div>
                <a href="{menu['url']}" target="_blank" class="menu-link">View Full Menu →</a>
            </div>
"""
        
        # Meat section
        meat_items = menu.get('meat', [])
        html += """
            <div class="category">
                <div class="category-header">
                    <span class="category-icon">🥩</span>
                    <span class="category-title">Meat</span>
                    <span class="category-count">{} items</span>
                </div>
                <div class="meat-section">
""".format(len(meat_items))
        
        if meat_items:
            html += "                    <ul class='items-list'>\n"
            for item in meat_items[:8]:
                html += f"                        <li>{item}</li>\n"
            if len(meat_items) > 8:
                html += f"                        <li class='more-items'>...and {len(meat_items) - 8} more</li>\n"
            html += "                    </ul>\n"
        else:
            html += "                    <p class='no-items'>No meat dishes today</p>\n"
        
        html += "                </div>\n            </div>\n"
        
        # Seafood section
        seafood_items = menu.get('seafood', [])
        html += """
            <div class="category">
                <div class="category-header">
                    <span class="category-icon">🐟</span>
                    <span class="category-title">Seafood</span>
                    <span class="category-count">{} items</span>
                </div>
                <div class="seafood-section">
""".format(len(seafood_items))
        
        if seafood_items:
            html += "                    <ul class='items-list'>\n"
            for item in seafood_items[:5]:
                html += f"                        <li>{item}</li>\n"
            if len(seafood_items) > 5:
                html += f"                        <li class='more-items'>...and {len(seafood_items) - 5} more</li>\n"
            html += "                    </ul>\n"
        else:
            html += "                    <p class='no-items'>No seafood today</p>\n"
        
        html += "                </div>\n            </div>\n"
        
        # Other section
        other_items = menu.get('other', [])
        html += """
            <div class="category">
                <div class="category-header">
                    <span class="category-icon">🥗</span>
                    <span class="category-title">Other</span>
                    <span class="category-count">{} items</span>
                </div>
                <div class="other-section">
""".format(len(other_items))
        
        if other_items:
            preview = other_items[:8]
            html += f"                    <p class='items-inline'>{', '.join(preview)}"
            if len(other_items) > 8:
                html += f" <span class='more-items'>...and {len(other_items) - 8} more</span>"
            html += "</p>\n"
        else:
            html += "                    <p class='no-items'>No other dishes today</p>\n"
        
        html += "                </div>\n            </div>\n"
        
        html += "        </div>\n"
    
    html += """
        <footer>
            <p>🤖 Auto-generated by Cafe Menu Bot</p>
        </footer>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate the weekly menu HTML file."""
    location = os.environ.get("CAFE_LOCATION", "palo-alto")
    
    print("🍽️  Cafe Menu Generator")
    print("=" * 40)
    print(f"Location: {location}")
    print(f"Output: {OUTPUT_FILE}")
    print()
    
    print("📥 Fetching weekly lunch menu...")
    weekly_menu = scrape_weekly_menu(location)
    
    print("📝 Generating HTML...")
    html_content = generate_html(weekly_menu, location)
    
    print("💾 Saving to Desktop...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Saved: {OUTPUT_FILE}")
    
    # Auto-open in browser
    print("🌐 Opening in browser...")
    subprocess.run(['open', OUTPUT_FILE])
    
    print()
    print("🎉 Done! Check your browser.")


if __name__ == "__main__":
    main()
