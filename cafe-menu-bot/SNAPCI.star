# SnapCI Configuration for Cafe Menu Bot
# This runs every Monday to send the weekly menu to Slack

# Weekly menu notification job
run(
    name = "send_weekly_menu",
    steps = [
        process("pip", "install", "-r", "requirements.txt"),
        process("python", "menu_scraper.py"),
    ],
    exec_requirements = {
        "os": "linux",
        "arch": "x86_64",
    },
    # Environment variables are set in SnapCI secrets
    # SLACK_WEBHOOK_URL must be configured in the repo settings
)

# Manual trigger via PR comment "/send-menu"
on_comment(
    name = "manual_menu_send",
    body = "/send-menu",
    execs = ["send_weekly_menu"],
)

# Scheduled trigger - Note: SnapCI scheduled triggers may need additional configuration
# Contact SnapCI team for cron-like scheduling setup
