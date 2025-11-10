#!/bin/bash
#
# Setup script for launchd automatic sync
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_NAME="com.reminders-to-gcal.sync"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PYTHON_PATH=$(which python3)
INTERVAL=3600  # Default: 1 hour (in seconds)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Reminders to Google Calendar Sync Setup"
echo "========================================"
echo ""

# Check if Python is available
if [ ! -f "$PYTHON_PATH" ]; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    echo "Please install Python 3 first"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $PYTHON_PATH"

# Ask for sync interval
echo ""
echo "How often should sync run?"
echo "1) Every 15 minutes"
echo "2) Every 30 minutes"
echo "3) Every hour (default)"
echo "4) Every 2 hours"
echo "5) Custom interval"
read -p "Choose [1-5] (default: 3): " choice

case $choice in
    1) INTERVAL=900 ;;
    2) INTERVAL=1800 ;;
    3) INTERVAL=3600 ;;
    4) INTERVAL=7200 ;;
    5)
        read -p "Enter interval in minutes: " custom_minutes
        INTERVAL=$((custom_minutes * 60))
        ;;
    *) INTERVAL=3600 ;;
esac

echo -e "${GREEN}✓${NC} Sync interval set to $((INTERVAL / 60)) minutes"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Generate plist file
echo ""
echo "Creating launchd plist file..."

cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON_PATH}</string>
        <string>${SCRIPT_DIR}/main.py</string>
        <string>sync</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>

    <key>StartInterval</key>
    <integer>${INTERVAL}</integer>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

echo -e "${GREEN}✓${NC} Created plist file: $PLIST_FILE"

# Unload if already loaded
if launchctl list | grep -q "$PLIST_NAME"; then
    echo ""
    echo "Unloading existing service..."
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Unloaded existing service"
fi

# Load the plist
echo ""
echo "Loading launchd service..."
launchctl load "$PLIST_FILE"

if launchctl list | grep -q "$PLIST_NAME"; then
    echo -e "${GREEN}✓${NC} Service loaded successfully"
else
    echo -e "${RED}✗${NC} Failed to load service"
    exit 1
fi

# Make main.py executable
chmod +x "$SCRIPT_DIR/main.py"

echo ""
echo "========================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "========================================"
echo ""
echo "The sync will run:"
echo "  - Immediately on system startup"
echo "  - Every $((INTERVAL / 60)) minutes"
echo ""
echo "Useful commands:"
echo "  - Check status:   launchctl list | grep $PLIST_NAME"
echo "  - View logs:      tail -f $SCRIPT_DIR/logs/sync.log"
echo "  - Stop service:   launchctl unload $PLIST_FILE"
echo "  - Start service:  launchctl load $PLIST_FILE"
echo "  - Remove service: rm $PLIST_FILE && launchctl unload $PLIST_FILE"
echo ""
echo "Note: First run will require Reminders access permission."
echo "      You may need to grant permission in System Settings."
echo ""
