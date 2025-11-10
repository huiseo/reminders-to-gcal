# 여러 기기에서 사용하기 가이드

## 현재 상황 정리

### ✅ 이미 해결된 것: 아이폰 미리알림 동기화

**좋은 소식**: 이미 자동으로 해결되어 있습니다! 🎉

**이유**:
- Apple 미리알림은 **iCloud로 자동 동기화**됩니다
- 아이폰에서 추가한 미리알림 → iCloud → 맥북의 미리알림 앱
- 맥북에서 추가한 미리알림 → iCloud → 아이폰의 미리알림 앱

**동작 방식**:
```
아이폰 미리알림 추가
    ↓ (iCloud 자동 동기화)
맥북 미리알림 앱에 자동 반영
    ↓ (1시간마다 자동 실행)
우리 동기화 스크립트 실행
    ↓
Google Calendar에 생성
```

**테스트 방법**:
1. 아이폰에서 미리알림 추가
2. 맥북 미리알림 앱에서 확인 (몇 초 안에 나타남)
3. 1시간 후 (또는 수동 실행) Google Calendar에 자동 생성

---

## 여러 맥북에서 사용하기

### 방법 1: iCloud Drive 활용 (권장)

**장점**:
- 설정 파일과 데이터베이스가 모든 맥북에서 자동 동기화
- OAuth 토큰 공유로 재인증 불필요
- 가장 간편함

**설정 방법**:

#### 1단계: 프로젝트를 iCloud Drive에 저장 (이미 완료!)

현재 위치가 이미 iCloud Drive 안입니다:
```
/Users/heeseo/Library/Mobile Documents/com~apple~CloudDocs/
13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/
reminders-to-gcal/
```

#### 2단계: 다른 맥북에서 설정

**다른 맥북 (13인치, 16인치 등)에서**:

1. **iCloud Drive 동기화 확인**
   ```bash
   # 같은 경로로 접근
   cd "/Users/YOUR_USERNAME/Library/Mobile Documents/com~apple~CloudDocs/13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/reminders-to-gcal"

   # 파일들이 보이는지 확인
   ls -la
   ```

2. **Python 의존성 설치**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **launchd 자동 실행 설정**

   다른 맥북의 경로에 맞게 plist 파일 생성:
   ```bash
   cat > ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist <<'EOF'
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.reminders-to-gcal.sync</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/Users/YOUR_USERNAME/Library/Mobile Documents/com~apple~CloudDocs/13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/reminders-to-gcal/main.py</string>
           <string>sync</string>
       </array>
       <key>WorkingDirectory</key>
       <string>/Users/YOUR_USERNAME/Library/Mobile Documents/com~apple~CloudDocs/13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/reminders-to-gcal</string>
       <key>StartInterval</key>
       <integer>3600</integer>
       <key>RunAtLoad</key>
       <true/>
       <key>StandardOutPath</key>
       <string>/Users/YOUR_USERNAME/Library/Mobile Documents/com~apple~CloudDocs/13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/reminders-to-gcal/logs/launchd.stdout.log</string>
       <key>StandardErrorPath</key>
       <string>/Users/YOUR_USERNAME/Library/Mobile Documents/com~apple~CloudDocs/13mac_file_sys/Personal/50.Work/90.Dev/Mac/ReminderSyncGoogle/reminders-to-gcal/logs/launchd.stderr.log</string>
       <key>EnvironmentVariables</key>
       <dict>
           <key>PATH</key>
           <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
       </dict>
   </dict>
   </plist>
   EOF

   # YOUR_USERNAME을 실제 사용자명으로 변경!
   ```

4. **launchd 활성화**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
   ```

5. **테스트**
   ```bash
   # 수동 실행 테스트
   python3 main.py sync
   ```

**작동 원리**:
- `credentials.json`, `data/token.json` 등이 iCloud로 동기화
- 데이터베이스(`data/mapping.db`)도 공유됨
- 어느 맥북에서든 동일한 설정 사용
- 중복 생성 방지 (같은 DB 사용)

---

### 방법 2: Git Repository 활용

**장점**:
- 버전 관리 가능
- 팀 협업 가능
- 설정 파일 추적 가능

**설정 방법**:

1. **Git Repository 초기화**
   ```bash
   cd /Users/heeseo/Work/ClaudeCode/reminders-to-gcal
   git init
   git add .
   git commit -m "Initial commit"

   # GitHub 등에 푸시
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **다른 맥북에서**
   ```bash
   git clone YOUR_REPO_URL
   cd reminders-to-gcal

   # Google OAuth 재인증 필요
   python3 -m pip install -r requirements.txt
   python3 main.py sync  # 첫 실행 시 OAuth 인증
   ```

**주의사항**:
- `credentials.json`과 `data/token.json`은 `.gitignore`에 포함되어 공유 안 됨
- 각 맥북에서 개별 인증 필요
- 데이터베이스도 공유 안 됨 (중복 생성 가능성 있음)

---

## 추천 구성

### 시나리오 1: 개인 사용 (여러 맥북)
→ **방법 1 (iCloud Drive)** 권장

### 시나리오 2: 팀 협업
→ **방법 2 (Git Repository)** 권장

---

## 전체 동작 흐름

```
┌─────────────┐
│   아이폰    │
│ 미리알림 추가│
└──────┬──────┘
       │ iCloud 자동 동기화 (몇 초)
       ↓
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  맥북 13인치 │      │  맥북 16인치 │      │  맥북 에어  │
│ 미리알림 앱  │ ←──→ │ 미리알림 앱  │ ←──→ │ 미리알림 앱  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                    │                    │
       │ 1시간마다          │ 1시간마다          │ 1시간마다
       │ 자동 실행          │ 자동 실행          │ 자동 실행
       ↓                    ↓                    ↓
┌─────────────────────────────────────────────────────────┐
│           동기화 스크립트 (iCloud Drive 공유)            │
│  - 같은 credentials.json                               │
│  - 같은 token.json (OAuth 인증 공유)                   │
│  - 같은 mapping.db (중복 방지)                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
              ┌─────────────────┐
              │ Google Calendar │
              │   단일 동기화   │
              └─────────────────┘
```

---

## FAQ

### Q1: 아이폰에서 추가한 미리알림이 Google Calendar에 안 나타나요
**A**: iCloud 동기화를 확인하세요
1. 아이폰 설정 → Apple ID → iCloud → 미리알림 활성화 확인
2. 맥북 시스템 설정 → Apple ID → iCloud → 미리알림 활성화 확인
3. 맥북 미리알림 앱에서 아이폰에서 추가한 항목 보이는지 확인
4. 최대 1시간 대기 (또는 `python3 main.py sync` 수동 실행)

### Q2: 여러 맥북에서 중복 생성되나요?
**A**: iCloud Drive 방식 사용 시 **중복 안 됨**
- 같은 `mapping.db` 사용
- UUID로 이미 동기화된 항목 추적
- 한 맥북에서 동기화되면 다른 맥북은 스킵

### Q3: 한 맥북이 꺼져있으면 어떻게 되나요?
**A**: 문제 없음
- 다른 맥북이 동기화 진행
- 켜진 맥북 중 하나라도 동작하면 OK
- 모든 맥북이 iCloud Drive로 연결되어 있으면 어느 맥북에서든 동기화 가능

### Q4: 맥북마다 다른 주기로 동기화하고 싶어요
**A**: 가능합니다
- 각 맥북의 plist 파일에서 `<integer>3600</integer>` 값 수정
- 예: 15분 = 900, 30분 = 1800, 1시간 = 3600, 2시간 = 7200

---

## 현재 설정 상태

✅ **자동 동기화 활성화됨**
- 주기: 1시간마다
- 부팅 시 자동 시작
- 로그: `/Users/heeseo/Work/ClaudeCode/reminders-to-gcal/logs/`

✅ **iCloud Drive 위치**
- 모든 맥북에서 접근 가능
- 설정 파일 자동 동기화
- OAuth 토큰 공유

✅ **아이폰 미리알림 연동**
- iCloud 자동 동기화
- 별도 설정 불필요
- 실시간 반영 (몇 초)

---

**작성일**: 2025-11-10
