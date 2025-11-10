#!/bin/bash
#
# Build Reminders to Google Calendar Mac App
#

set -e

echo "========================================"
echo "Building Reminders to Google Calendar App"
echo "========================================"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist "Reminders to GCal.app"

# Build with PyInstaller
echo "📦 Building app with PyInstaller..."
python3 -m PyInstaller \
    --name="Reminders to GCal" \
    --icon="icon.icns" \
    --windowed \
    --onefile \
    --osx-bundle-identifier="com.reminders-to-gcal.app" \
    --add-data="config.yaml:." \
    --add-data="src:src" \
    --add-data="icon.icns:." \
    --hidden-import="google.auth" \
    --hidden-import="google.oauth2" \
    --hidden-import="google_auth_oauthlib" \
    --hidden-import="googleapiclient" \
    --hidden-import="EventKit" \
    --hidden-import="Foundation" \
    --hidden-import="yaml" \
    --hidden-import="rumps" \
    --hidden-import="sqlite3" \
    --hidden-import="_sqlite3" \
    --collect-all="google" \
    --collect-all="googleapiclient" \
    --collect-all="google_auth_oauthlib" \
    menubar_app.py

# Post-processing
echo "✨ Post-processing..."

# Create necessary directories in .app bundle
APP_PATH="dist/Reminders to GCal.app"
RESOURCES_PATH="$APP_PATH/Contents/Resources"

mkdir -p "$RESOURCES_PATH/data"
mkdir -p "$RESOURCES_PATH/logs"

# Copy icon if not already there
if [ ! -f "$RESOURCES_PATH/icon.icns" ]; then
    cp icon.icns "$RESOURCES_PATH/"
fi

# Create .gitignore in data directory
cat > "$RESOURCES_PATH/data/.gitignore" <<EOF
*
!.gitignore
EOF

# Add LSUIElement to Info.plist to hide from Dock (menubar app only)
echo "🔧 Configuring as menubar-only app..."
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$APP_PATH/Contents/Info.plist" 2>/dev/null || \
/usr/libexec/PlistBuddy -c "Set :LSUIElement true" "$APP_PATH/Contents/Info.plist"

echo ""
echo "========================================"
echo "✅ Build Complete!"
echo "========================================"
echo ""
echo "App created at: $APP_PATH"
echo ""
echo "To test the app:"
echo "  open \"$APP_PATH\""
echo ""
echo "To install (copy to Applications):"
echo "  cp -r \"$APP_PATH\" /Applications/"
echo ""
echo "Note: On first run, you'll need to:"
echo "  1. Place credentials.json in the app's Resources folder"
echo "  2. Grant Reminders access permission"
echo "  3. Complete Google OAuth authentication"
echo ""
