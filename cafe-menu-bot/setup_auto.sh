#!/bin/bash
# Setup automatic weekly menu generation
# Runs every Monday at 8:00 AM and opens the menu in your browser

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.snap.cafe-menu-generator"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON_PATH="/Users/yyan5/miniconda3/bin/python"
LOG_PATH="/tmp/cafe-menu-generator.log"

echo "🍽️  Cafe Menu Auto-Generator Setup"
echo "==================================="
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create the launchd plist file
cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${SCRIPT_DIR}/generate_menu.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>${LOG_PATH}</string>
    
    <key>StandardErrorPath</key>
    <string>${LOG_PATH}</string>
</dict>
</plist>
EOF

echo "✅ Created: $PLIST_PATH"

# Unload if already loaded
launchctl unload "$PLIST_PATH" 2>/dev/null || true

# Load the new plist
launchctl load "$PLIST_PATH"

echo "✅ Scheduled task loaded!"
echo ""
echo "📅 Schedule: Every Monday at 8:00 AM"
echo "📄 Output: ~/Desktop/weekly_lunch_menu.html"
echo "📋 Log: $LOG_PATH"
echo ""
echo "Commands:"
echo "  Run now:    python '$SCRIPT_DIR/generate_menu.py'"
echo "  View logs:  tail -f $LOG_PATH"
echo "  Disable:    launchctl unload '$PLIST_PATH'"
echo ""
echo "🎉 Setup complete! The menu will auto-generate every Monday."
