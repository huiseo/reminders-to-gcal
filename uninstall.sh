#!/bin/bash
#
# Uninstall Reminders to GCal
# Complete removal of app and all related files
#

set -e

echo "=========================================="
echo "Reminders to GCal - 완전 제거"
echo "=========================================="
echo ""

# Function to prompt user
prompt_confirm() {
    while true; do
        read -p "$1 (y/n) " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "y 또는 n을 입력하세요.";;
        esac
    done
}

echo "다음 항목들이 제거됩니다:"
echo ""
echo "1. 앱 파일:"
echo "   /Applications/Reminders to GCal.app"
echo ""
echo "2. 사용자 설정:"
echo "   ~/.reminders-to-gcal-prefs.json"
echo ""
echo "3. Lock 파일:"
echo "   ~/.reminders-to-gcal.lock"
echo ""
echo "4. LaunchAgent (자동 동기화):"
echo "   ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist"
echo ""
echo "5. 로그인 항목 (자동 시작)"
echo ""

# Check what exists
app_exists=false
prefs_exists=false
lock_exists=false
launchagent_exists=false

if [ -d "/Applications/Reminders to GCal.app" ]; then
    app_exists=true
    echo "✓ 앱이 설치되어 있습니다"
fi

if [ -f ~/.reminders-to-gcal-prefs.json ]; then
    prefs_exists=true
    echo "✓ 사용자 설정이 있습니다"
fi

if [ -f ~/.reminders-to-gcal.lock ]; then
    lock_exists=true
    echo "✓ Lock 파일이 있습니다"
fi

if [ -f ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist ]; then
    launchagent_exists=true
    echo "✓ LaunchAgent가 설치되어 있습니다"
fi

echo ""
echo "⚠️  주의: 앱 내부 데이터도 모두 삭제됩니다:"
echo "   - Google OAuth 토큰"
echo "   - UUID 매핑 데이터베이스"
echo "   - 동기화 로그"
echo ""

if ! prompt_confirm "정말 제거하시겠습니까?"; then
    echo "취소되었습니다."
    exit 0
fi

echo ""
echo "제거 중..."
echo ""

# 1. Stop and remove LaunchAgent
if [ "$launchagent_exists" = true ]; then
    echo "🔧 LaunchAgent 중지 및 제거 중..."
    launchctl unload ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist 2>/dev/null || true
    rm -f ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
    echo "   ✓ LaunchAgent 제거됨"
fi

# 2. Remove login item
echo "🔧 로그인 항목 제거 중..."
osascript -e 'tell application "System Events" to delete login item "Reminders to GCal"' 2>/dev/null || true
echo "   ✓ 로그인 항목 제거됨"

# 3. Kill running app
echo "🔧 실행 중인 앱 종료 중..."
pkill -9 -f "Reminders to GCal" 2>/dev/null || true
echo "   ✓ 앱 종료됨"

# 4. Remove lock file
if [ "$lock_exists" = true ]; then
    echo "🔧 Lock 파일 제거 중..."
    rm -f ~/.reminders-to-gcal.lock
    echo "   ✓ Lock 파일 제거됨"
fi

# 5. Remove user preferences
if [ "$prefs_exists" = true ]; then
    echo "🔧 사용자 설정 제거 중..."
    rm -f ~/.reminders-to-gcal-prefs.json
    echo "   ✓ 사용자 설정 제거됨"
fi

# 6. Remove app
if [ "$app_exists" = true ]; then
    echo "🔧 앱 제거 중..."
    rm -rf "/Applications/Reminders to GCal.app"
    echo "   ✓ 앱 제거됨"
fi

# 7. Remove cache (optional)
echo "🔧 캐시 제거 중..."
rm -rf ~/Library/Caches/com.apple.python/*/reminders-to-gcal 2>/dev/null || true
echo "   ✓ 캐시 제거됨"

echo ""
echo "=========================================="
echo "✅ 제거 완료!"
echo "=========================================="
echo ""
echo "Reminders to GCal이 완전히 제거되었습니다."
echo ""
echo "💡 재설치하려면:"
echo "   1. DMG 파일을 다시 열기"
echo "   2. 앱을 Applications 폴더로 드래그"
echo ""
