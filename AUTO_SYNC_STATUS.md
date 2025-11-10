# 자동 동기화 상태

## ✅ 자동 실행 활성화 완료!

**마지막 확인 시간**: 2025-11-10 11:44:22

### 현재 설정

- **서비스 이름**: `com.reminders-to-gcal.sync`
- **상태**: ✅ 실행 중
- **동기화 주기**: 1시간마다 (3600초)
- **부팅 시 자동 시작**: ✅ 활성화
- **작업 디렉토리**: `/Users/heeseo/Work/ClaudeCode/reminders-to-gcal`

### 자동 실행 확인

```bash
# 서비스 상태 확인
launchctl list | grep reminders-to-gcal

# 출력: -	0	com.reminders-to-gcal.sync
# (0 = 정상 실행 중)
```

### 동작 방식

1. **부팅 시**: 맥북 켜면 자동으로 첫 동기화 실행
2. **이후**: 1시간마다 자동으로 동기화
3. **백그라운드**: 화면 꺼져 있어도 계속 작동

### 로그 확인 방법

```bash
# 실시간 로그 보기
tail -f /Users/heeseo/Work/ClaudeCode/reminders-to-gcal/logs/sync.log

# 최근 로그 확인
tail -20 /Users/heeseo/Work/ClaudeCode/reminders-to-gcal/logs/sync.log

# launchd 에러 로그 확인
tail -20 /Users/heeseo/Work/ClaudeCode/reminders-to-gcal/logs/launchd.stderr.log
```

### 테스트 방법

1. **미리알림 추가**:
   - Mac 미리알림 앱 또는 아이폰에서 미리알림 추가
   - 제목: "자동 동기화 테스트"
   - 날짜/시간 설정 (선택)

2. **자동 동기화 대기**:
   - 최대 1시간 대기 (다음 자동 실행까지)
   - 또는 수동으로 즉시 실행: `python3 main.py sync`

3. **Google Calendar 확인**:
   - Google Calendar 열기
   - "자동 동기화 테스트" 이벤트 확인

### 수동 제어 명령어

```bash
# 즉시 동기화 실행 (자동 실행 대기 안하고)
launchctl kickstart gui/$(id -u)/com.reminders-to-gcal.sync

# 자동 실행 일시 중지
launchctl unload /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist

# 자동 실행 다시 활성화
launchctl load /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist

# 서비스 완전 삭제 (자동 실행 해제)
launchctl unload /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
rm /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
```

### 다음 자동 실행 시간

현재 시간: 11:44
다음 실행: **12:44** (약 1시간 후)

### 문제 해결

**Q: 자동으로 실행 안 되는 것 같아요**
```bash
# 1. 서비스 상태 확인
launchctl list | grep reminders-to-gcal

# 2. 에러 로그 확인
tail -50 /Users/heeseo/Work/ClaudeCode/reminders-to-gcal/logs/launchd.stderr.log

# 3. 재시작
launchctl unload /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
launchctl load /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
```

**Q: 즉시 동기화하고 싶어요**
```bash
cd /Users/heeseo/Work/ClaudeCode/reminders-to-gcal
python3 main.py sync
```

**Q: 동기화 주기를 변경하고 싶어요**
```bash
# plist 파일 편집
nano /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist

# <integer>3600</integer> 부분 수정:
# 15분 = 900
# 30분 = 1800
# 1시간 = 3600
# 2시간 = 7200

# 변경 후 재시작
launchctl unload /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
launchctl load /Users/heeseo/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
```

---

## ✅ 확인 완료!

자동 동기화가 정상적으로 작동하고 있습니다.
- 방금 11:44:22에 자동 실행됨
- 다음 실행은 1시간 후 (12:44경)
- 부팅 시에도 자동으로 시작됨

**미리알림 추가 → 1시간 이내 자동으로 Google Calendar에 동기화됩니다!** 🎉
