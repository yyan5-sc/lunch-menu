#!/bin/bash
# Setup script for Cafe Menu Bot
# This script helps configure the weekly menu notification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.snap.cafe-menu-bot"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON_PATH="/Users/yyan5/miniconda3/bin/python"
LOG_PATH="/tmp/cafe-menu-bot.log"

echo "🍽️  Cafe Menu Bot Setup"
echo "========================"
echo ""
echo "Target Slack Channel: #south-bay-lunch-bot"
echo ""

# Check if webhook URL is provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your Slack Webhook URL"
    echo ""
    echo "Usage: ./setup.sh <SLACK_WEBHOOK_URL>"
    echo ""
    echo "To get a Webhook URL:"
    echo "  1. Go to https://api.slack.com/apps"
    echo "  2. Create New App → From scratch"
    echo "  3. Name it 'Cafe Menu Bot', select your workspace"
    echo "  4. Click 'Incoming Webhooks' in left menu"
    echo "  5. Enable 'Activate Incoming Webhooks'"
    echo "  6. Click 'Add New Webhook to Workspace'"
    echo "  7. Select channel: #south-bay-lunch-bot"
    echo "  8. Copy the Webhook URL"
    echo ""
    echo "Then run: ./setup.sh https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    exit 1
fi

WEBHOOK_URL="$1"

echo "📝 Creating launchd plist for weekly scheduling..."

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
        <string>${SCRIPT_DIR}/menu_scraper.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>SLACK_WEBHOOK_URL</key>
        <string>${WEBHOOK_URL}</string>
        <key>CAFE_LOCATION</key>
        <string>palo-alto</string>
    </dict>
    
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
echo "📍 Channel: #south-bay-lunch-bot"
echo "📄 Log file: $LOG_PATH"
echo ""
echo "Commands:"
echo "  Test now:     cd '$SCRIPT_DIR' && SLACK_WEBHOOK_URL='$WEBHOOK_URL' python menu_scraper.py"
echo "  View logs:    tail -f $LOG_PATH"
echo "  Stop:         launchctl unload '$PLIST_PATH'"
echo "  Restart:      launchctl unload '$PLIST_PATH' && launchctl load '$PLIST_PATH'"
echo ""
echo "🎉 Setup complete!"
