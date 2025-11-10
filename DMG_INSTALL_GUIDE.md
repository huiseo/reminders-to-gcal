# Reminders to GCal - 간단 설치 가이드 (DMG)

## 🎁 DMG 파일로 3단계 설치!

**파일**: `Reminders-to-GCal.dmg` (21MB)

---

## 🚀 설치 방법 (3단계)

### 1단계: DMG 파일 다운로드/복사

**옵션 A - iCloud Drive에서 다운로드**
```
iCloud Drive → 13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/
→ Reminders-to-GCal.dmg 찾기
```

**옵션 B - AirDrop으로 전송**
```
다른 맥에서:
1. Finder에서 Reminders-to-GCal.dmg 우클릭
2. "공유" → "AirDrop"
3. 받는 맥 선택
```

**옵션 C - USB/외장 하드**
```
DMG 파일을 USB에 복사 → 다른 맥에 연결
```

---

### 2단계: DMG 마운트

**더블클릭!**
```
Reminders-to-GCal.dmg 더블클릭
→ 디스크 이미지가 마운트됨
→ Finder 창 자동으로 열림
```

**또는 터미널에서**:
```bash
open Reminders-to-GCal.dmg
```

---

### 3단계: 앱 설치

**방법 1: 드래그 앤 드롭 (가장 쉬움)**
```
1. 마운트된 Finder 창에서 "Reminders to GCal.app" 찾기
2. Applications 폴더 열기 (Cmd+Shift+A)
3. 앱을 Applications 폴더로 드래그
4. 복사 완료 대기
5. 완료!
```

**방법 2: 터미널에서**
```bash
# DMG 마운트
hdiutil attach Reminders-to-GCal.dmg

# 앱 복사
cp -r "/Volumes/Reminders to GCal/Reminders to GCal.app" /Applications/

# DMG 언마운트
hdiutil detach "/Volumes/Reminders to GCal"
```

---

## ▶️ 첫 실행

### 1. 앱 열기

**Finder에서**:
```
Applications 폴더 → "Reminders to GCal" 더블클릭
```

**또는 Spotlight**:
```
Cmd+Space → "Reminders" 입력 → Enter
```

### 2. 보안 경고 (첫 실행 시)

**"열 수 없습니다" 경고가 나타나면**:

```
1. 시스템 설정 열기
2. 개인정보 보호 및 보안 클릭
3. "확인 없이 열기" 버튼 클릭
4. 다시 앱 더블클릭
```

**또는 터미널에서 보안 속성 제거**:
```bash
xattr -cr /Applications/Reminders\ to\ GCal.app
```

### 3. 상단 메뉴바 확인

앱이 성공적으로 실행되면:
```
✅ 상단 메뉴바에 "R→GCal" 아이콘 나타남
```

---

## 🔐 초기 설정 (첫 실행 시 1회)

### 1. Google OAuth 인증

메뉴바 "R→GCal" 클릭 → "Sync Now" 클릭 시:

```
1. 브라우저 자동으로 열림
2. Google 계정 로그인
3. "Reminders to GCal에서 Google Calendar 접근 허용" → "허용"
4. "인증 완료" 페이지 확인
5. 브라우저 닫기
```

**중요**: OAuth 인증은 **맥별로 1회만** 필요합니다.

### 2. 미리알림 권한

처음 동기화 시도 시:

```
1. "미리알림 접근 권한 필요" 다이얼로그 나타남
2. 시스템 설정 열기
3. 개인정보 보호 및 보안 → 미리알림
4. "Reminders to GCal" 체크박스 활성화
5. 앱 재시작
```

---

## 📱 사용 방법

### 메뉴바 앱

```
R→GCal (상단 메뉴바 아이콘 클릭)
├─ Sync Now                    → 즉시 동기화
├─ Last Sync: 12:01 (1↑ 0↻ 0↓) → 마지막 동기화 시간
├─ ───────────────
├─ View Logs                   → 로그 파일 열기
├─ Open Reminders              → 미리알림 앱 열기
├─ Open Google Calendar        → Google Calendar 열기
├─ ───────────────
├─ About                       → 앱 정보
└─ Quit                        → 앱 종료
```

### 사용 팁

**수동 동기화**:
- 메뉴바 아이콘 클릭 → "Sync Now"
- 알림으로 결과 확인

**자동 시작 설정** (선택):
```
시스템 설정 → 일반 → 로그인 항목
→ "+" 클릭 → "Reminders to GCal" 선택
→ 맥북 켤 때마다 자동 시작
```

---

## 🔄 자동 동기화 설정 (고급)

메뉴바 앱은 **수동 실행용**입니다.

**정기적 자동 동기화**를 원하면 (예: 1시간마다):

### 옵션 1: Automator 사용 (간단)

```
1. Automator 앱 열기
2. "캘린더 알람" 선택
3. "애플리케이션 실행" 액션 추가
4. "Reminders to GCal" 선택
5. "파일" → "저장"
6. 캘린더 앱에서 1시간마다 반복으로 설정
```

### 옵션 2: launchd 사용 (추천)

터미널에서 실행:

```bash
# launchd 설정 파일 생성
cat > ~/Library/LaunchAgents/com.reminders-to-gcal.auto.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.reminders-to-gcal.auto</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/open</string>
        <string>-g</string>
        <string>/Applications/Reminders to GCal.app</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 활성화
launchctl load ~/Library/LaunchAgents/com.reminders-to-gcal.auto.plist
```

→ 1시간(3600초)마다 앱 자동 실행

---

## 🔧 문제 해결

### Q: "손상되어 열 수 없습니다" 오류

**해결 방법 1 - 시스템 설정**:
```
시스템 설정 → 개인정보 보호 및 보안
→ "확인 없이 열기" 클릭
```

**해결 방법 2 - 터미널**:
```bash
xattr -cr /Applications/Reminders\ to\ GCal.app
```

---

### Q: Google 인증이 안 돼요

**확인**:
```bash
# credentials.json 파일 확인
ls /Applications/Reminders\ to\ GCal.app/Contents/Resources/credentials.json
```

**없으면**:
```
원본 DMG에는 credentials.json이 포함되어 있습니다.
앱을 재설치하거나, 원본에서 복사하세요.
```

---

### Q: 미리알림 권한 오류

**해결**:
```
1. 시스템 설정 → 개인정보 보호 및 보안 → 미리알림
2. "Reminders to GCal" 찾아서 체크
3. 앱 재시작
```

---

### Q: 동기화가 안 돼요

**확인 순서**:

1. **인터넷 연결** 확인
2. **미리알림 권한** 확인
3. **Google 인증** 확인
4. **로그 확인**:
   ```
   메뉴바 → "View Logs" 클릭
   또는
   Console 앱 → "Reminders to GCal" 검색
   ```

---

## 📦 앱 정보

- **이름**: Reminders to GCal
- **버전**: 1.0
- **크기**: 21MB
- **요구사항**: macOS 10.13 (High Sierra) 이상
- **Python 필요**: ❌ 없음 (독립 실행)
- **인터넷**: ✅ 필요 (Google Calendar API)

---

## 🗑️ 제거 방법

### 간편 제거 (추천)

**자동 제거 스크립트 사용:**

```bash
cd /Users/heeseo/Work/ClaudeCode/reminders-to-gcal
./uninstall.sh
```

제거되는 항목:
- ✅ 앱 파일 (/Applications/Reminders to GCal.app)
- ✅ 사용자 설정 (~/.reminders-to-gcal-prefs.json)
- ✅ Lock 파일 (~/.reminders-to-gcal.lock)
- ✅ LaunchAgent (~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist)
- ✅ 로그인 항목
- ✅ OAuth 토큰 및 데이터베이스
- ✅ 캐시 파일

---

### 수동 제거

#### 앱만 제거 (데이터는 유지)

```bash
rm -rf /Applications/Reminders\ to\ GCal.app
```

#### 완전 제거 (모든 데이터 삭제)

```bash
# 1. 앱 종료
pkill -9 -f "Reminders to GCal"

# 2. 앱 제거
rm -rf /Applications/Reminders\ to\ GCal.app

# 3. LaunchAgent 제거
launchctl unload ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist 2>/dev/null
rm ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist 2>/dev/null

# 4. 로그인 항목 제거
osascript -e 'tell application "System Events" to delete login item "Reminders to GCal"'

# 5. 사용자 설정 제거
rm -f ~/.reminders-to-gcal-prefs.json
rm -f ~/.reminders-to-gcal.lock

# 6. 캐시 제거
rm -rf ~/Library/Caches/com.apple.python/*/reminders-to-gcal
```

---

## 🔄 업데이트 방법

1. **기존 앱 제거**: Applications 폴더에서 삭제
2. **새 DMG 다운로드**: 새 버전 DMG 받기
3. **재설치**: 위의 설치 방법 반복
4. **OAuth 재인증**: 필요 없음 (자동 유지)

---

## 📝 요약

### 설치 3단계:
1. DMG 더블클릭
2. 앱을 Applications 폴더로 드래그
3. 완료!

### 첫 실행:
1. 보안 경고 → "확인 없이 열기"
2. Google OAuth 인증
3. 미리알림 권한 허용

### 사용:
- 메뉴바 "R→GCal" 클릭
- "Sync Now" 클릭
- 완료!

---

## 💡 다른 맥에 배포

**DMG 파일만 공유하면 됩니다!**

- ✅ AirDrop으로 전송
- ✅ iCloud Drive에 업로드
- ✅ 이메일/메신저로 전송
- ✅ USB에 복사

**받는 사람**:
1. DMG 더블클릭
2. 앱을 Applications로 드래그
3. 끝!

---

**작성일**: 2025-11-10
**파일명**: Reminders-to-GCal.dmg
**위치**: iCloud Drive에 저장됨
