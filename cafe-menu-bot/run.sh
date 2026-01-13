#!/bin/bash
# Quick run script for Cafe Menu Bot
# Usage: ./run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check for required environment variable
if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "❌ Error: SLACK_WEBHOOK_URL environment variable is not set"
    echo ""
    echo "Please set it before running:"
    echo "  export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'"
    echo ""
    exit 1
fi

# Install dependencies if needed
if ! python -c "import requests, bs4" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the scraper
echo "🍽️ Starting Cafe Menu Bot..."
python menu_scraper.py
