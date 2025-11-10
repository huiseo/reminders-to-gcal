# Reminders to GCal - Mac App 설치 가이드

## 🎉 독립 실행 가능한 Mac 앱 완성!

Python 설치 없이 다른 맥에서 바로 실행 가능한 앱입니다.

---

## 📦 앱 파일 위치

빌드된 앱: `dist/Reminders to GCal.app`
설치된 앱: `/Applications/Reminders to GCal.app`

---

## 🚀 다른 맥에 설치하기

### 방법 1: 직접 복사 (가장 간단)

#### 1단계: 앱 파일 전송

**옵션 A - AirDrop**
1. Finder에서 `dist/Reminders to GCal.app` 찾기
2. 마우스 우클릭 → "공유" → "AirDrop"
3. 다른 맥 선택

**옵션 B - iCloud Drive**
1. `dist/Reminders to GCal.app`를 iCloud Drive에 복사
2. 다른 맥에서 iCloud Drive 열기
3. 앱 다운로드 대기

**옵션 C - USB/외장 하드**
1. 앱을 USB에 복사
2. 다른 맥에 USB 연결
3. 앱 복사

#### 2단계: 설치

```bash
# 터미널에서
cp -r "Reminders to GCal.app" /Applications/

# 또는 Finder에서 드래그앤드롭
```

#### 3단계: 첫 실행

1. **Applications 폴더** 열기
2. **"Reminders to GCal"** 찾기
3. **더블클릭**

**보안 경고가 나타나면**:
- "열 수 없습니다" 메시지 → 시스템 설정 열기
- 시스템 설정 → 개인정보 보호 및 보안 → "확인 없이 열기" 클릭
- 다시 앱 더블클릭

4. **상단 메뉴바에 "R→GCal" 아이콘 확인**

#### 4단계: Google OAuth 인증 (첫 실행 시 1회)

1. 메뉴바 아이콘 클릭 → "Sync Now"
2. 브라우저가 자동으로 열림
3. Google 계정 로그인
4. "Reminders to GCal에서 Google Calendar 접근 허용" → "허용" 클릭
5. "인증 완료" 페이지 확인
6. 완료!

---

### 방법 2: 개발자용 빌드 (소스코드부터)

다른 맥에서 직접 빌드하려면:

```bash
# 1. 프로젝트 클론/복사
cd /path/to/reminders-to-gcal

# 2. 의존성 설치
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller rumps pillow

# 3. 빌드
./build_app.sh

# 4. 설치
cp -r "dist/Reminders to GCal.app" /Applications/
```

---

## 🖥️ 앱 사용 방법

### 메뉴바 앱

앱을 실행하면 **상단 메뉴바에 "R→GCal" 아이콘**이 나타납니다.

#### 메뉴 항목:

```
R→GCal
├─ Sync Now                    → 즉시 동기화 실행
├─ Last Sync: 11:44 (1↑ 0↻ 0↓) → 마지막 동기화 시간 및 통계
├─ ───────────────
├─ View Logs                   → 로그 파일 열기 (Console 앱)
├─ Open Reminders              → 미리알림 앱 열기
├─ Open Google Calendar        → Google Calendar 웹 열기
├─ ───────────────
├─ About                       → 앱 정보
└─ Quit                        → 앱 종료
```

#### 사용 팁:

- **"Sync Now"**: 수동으로 즉시 동기화
- **자동 동기화**: launchd 설정 필요 (아래 참고)
- **동기화 중**: 아이콘이 "R→GCal ⟳"로 바뀜
- **완료 알림**: macOS 알림으로 결과 표시

---

## 🔄 자동 동기화 설정 (선택사항)

앱은 메뉴바에서 수동 실행용입니다. 자동 동기화를 원하면:

### 옵션 A: 로그인 시 앱 자동 시작

1. 시스템 설정 → 일반 → 로그인 항목
2. "+" 클릭
3. "Reminders to GCal" 선택
4. 추가

→ 맥북 켤 때마다 메뉴바 앱 자동 시작

### 옵션 B: 정기적 자동 동기화 (launchd)

터미널에서 실행:

```bash
cd /Applications/Reminders\ to\ GCal.app/Contents/Resources

# launchd 설정 생성
cat > ~/Library/LaunchAgents/com.reminders-to-gcal.app.sync.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.reminders-to-gcal.app.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/osascript</string>
        <string>-e</string>
        <string>tell application "Reminders to GCal" to activate</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 활성화
launchctl load ~/Library/LaunchAgents/com.reminders-to-gcal.app.sync.plist
```

→ 1시간마다 자동으로 앱 실행 (메뉴바 아이콘 클릭해서 Sync Now 누르는 것과 동일)

---

## 🔧 문제 해결

### Q: "손상되어 열 수 없습니다" 오류

**원인**: macOS Gatekeeper 보안 정책

**해결**:
```bash
# 터미널에서
xattr -cr /Applications/Reminders\ to\ GCal.app

# 그리고 다시 실행
```

또는:
1. 시스템 설정 → 개인정보 보호 및 보안
2. "확인 없이 열기" 클릭

---

### Q: OAuth 인증이 안 돼요

**확인사항**:
1. `credentials.json` 파일이 있는지 확인
   ```bash
   ls /Applications/Reminders\ to\ GCal.app/Contents/Resources/credentials.json
   ```

2. credentials.json이 없으면:
   - 원본 맥에서 복사
   - 또는 Google Cloud Console에서 새로 다운로드

3. 복사 방법:
   ```bash
   cp credentials.json /Applications/Reminders\ to\ GCal.app/Contents/Resources/
   ```

---

### Q: 미리알림 권한이 필요합니다

**해결**:
1. 시스템 설정 → 개인정보 보호 및 보안 → 미리알림
2. "Reminders to GCal" 체크박스 활성화
3. 앱 재시작

---

### Q: 로그는 어디서 확인하나요?

```bash
# 앱 내부 로그
tail -f /Applications/Reminders\ to\ GCal.app/Contents/Resources/logs/sync.log

# 또는 메뉴바 → "View Logs"
```

---

### Q: 앱 업데이트는 어떻게 하나요?

1. 기존 앱 삭제:
   ```bash
   rm -rf /Applications/Reminders\ to\ GCal.app
   ```

2. 새 앱 복사:
   ```bash
   cp -r "새로운\ Reminders\ to\ GCal.app" /Applications/
   ```

3. OAuth 토큰은 유지됨 (재인증 불필요)

---

## 📊 앱 크기 및 요구사항

- **앱 크기**: ~70MB
- **macOS 버전**: macOS 10.13 (High Sierra) 이상
- **Python 필요**: ❌ 없음 (독립 실행 가능)
- **인터넷 연결**: ✅ 필요 (Google Calendar API)

---

## 🆚 CLI 버전 vs 앱 버전

### CLI 버전 (기존)
- ✅ Python 설치 필요
- ✅ launchd로 백그라운드 자동 실행
- ✅ 더 작은 크기
- ❌ 수동 실행 불편

### 앱 버전 (새로 만든 것!)
- ✅ Python 설치 불필요
- ✅ 메뉴바에서 즉시 동기화
- ✅ 시각적 피드백 (알림)
- ✅ 다른 맥에 쉽게 배포
- ❌ 조금 더 큰 크기 (~70MB)

**추천**: 두 가지 모두 사용 가능!
- 앱: 수동 동기화용
- CLI + launchd: 자동 동기화용

---

## 🎁 배포 패키지 만들기

여러 맥에 배포하려면:

### DMG 파일 생성

```bash
# 1. DMG 이미지 생성
hdiutil create -volname "Reminders to GCal" -srcfolder "dist/Reminders to GCal.app" -ov -format UDZO "Reminders-to-GCal.dmg"

# 2. 다른 맥에서
# - DMG 파일 더블클릭
# - 앱을 Applications 폴더로 드래그
# - 완료!
```

### ZIP 파일 생성

```bash
# 압축
cd dist
zip -r "Reminders-to-GCal.zip" "Reminders to GCal.app"

# 배포
# - ZIP 파일 공유
# - 압축 해제 후 Applications 폴더로 이동
```

---

## 📝 요약

### 다른 맥에서 3단계로 설치:

1. **앱 복사**: AirDrop, iCloud Drive, 또는 USB
2. **Applications 폴더에 설치**: 드래그앤드롭
3. **첫 실행**: 더블클릭 → Google OAuth 인증

### 완료!

- 상단 메뉴바에 "R→GCal" 아이콘
- 클릭 → "Sync Now" → 즉시 동기화
- Python 설치 불필요
- 독립 실행 가능

---

**작성일**: 2025-11-10
**버전**: 1.0
**앱 크기**: ~70MB
**지원 OS**: macOS 10.13+
