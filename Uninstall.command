#!/bin/bash
#
# Uninstall Reminders to GCal
# Double-click to completely remove the app and all settings
#

# Change to script directory
cd "$(dirname "$0")"

echo ""
echo "=========================================="
echo "  Reminders to GCal - 완전 제거"
echo "=========================================="
echo ""
echo "다음 항목들이 제거됩니다:"
echo ""
echo "  ✓ /Applications/Reminders to GCal.app"
echo "  ✓ 사용자 설정 파일"
echo "  ✓ 자동 실행 설정"
echo "  ✓ 로그인 항목"
echo "  ✓ 캐시 파일"
echo ""
echo "⚠️  주의: OAuth 토큰과 동기화 데이터도 삭제됩니다."
echo ""
read -p "계속하시겠습니까? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "취소되었습니다."
    echo ""
    read -p "아무 키나 눌러서 종료..." -n 1
    exit 0
fi

echo ""
echo "제거 중..."
echo ""

# Stop and kill app
echo "→ 앱 종료 중..."
pkill -9 -f "Reminders to GCal" 2>/dev/null || true

# Remove LaunchAgent
echo "→ 자동 실행 설정 제거 중..."
launchctl unload ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist 2>/dev/null || true
rm -f ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist 2>/dev/null || true

# Remove login item
echo "→ 로그인 항목 제거 중..."
osascript -e 'tell application "System Events" to delete login item "Reminders to GCal"' 2>/dev/null || true

# Remove preferences
echo "→ 사용자 설정 제거 중..."
rm -f ~/.reminders-to-gcal-prefs.json 2>/dev/null || true
rm -f ~/.reminders-to-gcal.lock 2>/dev/null || true

# Remove app
echo "→ 앱 제거 중..."
rm -rf "/Applications/Reminders to GCal.app" 2>/dev/null || true

# Remove cache
echo "→ 캐시 제거 중..."
rm -rf ~/Library/Caches/com.apple.python/*/reminders-to-gcal 2>/dev/null || true

echo ""
echo "=========================================="
echo "  ✅ 제거 완료!"
echo "=========================================="
echo ""
echo "Reminders to GCal이 완전히 제거되었습니다."
echo ""
echo "💡 재설치하려면 DMG 파일을 다시 열어서"
echo "   앱을 Applications 폴더로 드래그하세요."
echo ""
read -p "아무 키나 눌러서 종료..." -n 1
echo ""
