# Reminders to GCal - 기능 목록

## ✨ 최신 버전 2.0 - 전체 기능

### 🎯 핵심 기능

#### 1. **동기화 (Sync)**
- **수동 동기화**: 메뉴바에서 "Sync Now" 클릭
- **자동 동기화**: 설정한 간격으로 자동 동기화 (15분/30분/1시간/2시간)
- **실시간 상태 표시**: 동기화 중 메뉴바 아이콘이 회전 표시 (⟳)
- **동기화 결과**: 생성(↑), 업데이트(↻), 삭제(↓) 개수 표시

#### 2. **환경설정 (Preferences)**
메뉴에서 "Preferences..." 선택

**설정 가능 항목:**
- ✅ 자동 동기화 간격 (분 단위)
  - 0 = 수동만
  - 15 = 15분마다
  - 30 = 30분마다
  - 60 = 1시간마다
  - 120 = 2시간마다
- ✅ 알림 표시 여부
- ✅ 완료된 미리알림 동기화 여부

**환경설정 파일 위치**: `~/.reminders-to-gcal-prefs.json`

#### 3. **로그인 시 자동 시작**
- macOS 시스템 환경설정과 연동
- AppleScript를 통해 로그인 항목에 자동 추가/제거
- 앱이 백그라운드에서 자동 실행

#### 4. **단일 인스턴스 실행**
- 앱이 이미 실행 중이면 추가 실행 방지
- fcntl lock 방식 사용
- 중복 실행 시 메시지 표시

---

### 🎨 사용자 인터페이스

#### 메뉴바 아이콘
- **기본**: "R→GCal"
- **동기화 중**: "R→GCal ⟳"

#### 메뉴 구조
```
R→GCal
├─ Sync Now                        → 즉시 동기화
├─ Last Sync: 12:54 (1↑ 0↻ 0↓)   → 마지막 동기화 정보
├─ ───────────────
├─ Preferences...                  → 환경설정
├─ ───────────────
├─ View Logs                       → 로그 확인
├─ Open Reminders                  → 미리알림 앱 열기
├─ Open Google Calendar            → Google Calendar 열기
├─ ───────────────
├─ Help                            → 도움말
├─ About                           → 앱 정보
└─ Quit                            → 종료
```

---

### 🔔 알림 (Notifications)

#### 성공 알림
- 제목: "Sync Complete"
- 부제목: "X created, Y updated"
- 메시지: "Total: Z reminders"

#### 에러 알림
- 제목: "Sync Complete with Errors"
- 부제목: "X errors occurred"
- 메시지: "Check logs for details"

#### 설정 알림
- 환경설정 변경 시 알림 표시

---

### 🛠️ 에러 처리 및 복구

#### Configuration Error
파일이 없거나 설정 오류 시:
- **옵션 1**: View Guide - 설치 가이드 열기
- **옵션 2**: Open App Folder - 앱 폴더 열기
- **취소**: 무시

#### Sync Error
동기화 중 에러 발생 시:
- **옵션 1**: Retry - 재시도
- **옵션 2**: Re-authenticate - Google 인증 재설정
- **취소**: 무시

#### 인증 재설정 (Re-authenticate)
- Google OAuth token 삭제
- 다음 동기화 시 재인증 필요

---

### 📖 Help 메뉴

#### 옵션
- **User Guide**: 사용자 가이드 열기 (DMG_INSTALL_GUIDE.md)
- **Report Issue**: GitHub Issues 페이지 열기
- **취소**: 닫기

---

### 🔍 로그 및 디버깅

#### 로그 보기
- 메뉴에서 "View Logs" 클릭
- macOS Console 앱으로 열림
- 로그 파일 위치: `logs/sync.log`

#### 로그 내용
- 동기화 시작/종료 시간
- 처리된 미리알림 개수
- 생성/업데이트/삭제된 이벤트
- 에러 메시지 및 스택 트레이스

---

### ⚙️ 고급 기능

#### 1. 자동 동기화 타이머
- rumps.Timer 사용
- 백그라운드에서 주기적 실행
- 앱 종료 시 타이머 자동 중지

#### 2. 백그라운드 동기화
- threading.Thread로 비동기 처리
- UI 블록 방지
- 동기화 중 메뉴바 아이콘 애니메이션

#### 3. 상태 저장
- 마지막 동기화 시간 저장
- 동기화 통계 (생성/업데이트/삭제) 저장
- 사용자 설정 JSON 파일로 저장

---

## 🔐 보안 및 권한

### 필요한 권한
1. **미리알림 접근 권한**
   - 시스템 설정 → 개인정보 보호 및 보안 → 미리알림
   - "Reminders to GCal" 체크

2. **Google Calendar API 권한**
   - OAuth 2.0 인증
   - 브라우저를 통한 로그인
   - token.json에 토큰 저장

3. **알림 권한**
   - 시스템 알림 센터
   - 자동으로 요청됨

---

## 📦 파일 구조

```
/Applications/Reminders to GCal.app/
├── Contents/
│   ├── MacOS/
│   │   └── Reminders to GCal        (실행 파일)
│   ├── Resources/
│   │   ├── icon.icns                (앱 아이콘)
│   │   ├── config.yaml              (앱 설정)
│   │   ├── credentials.json         (Google OAuth 클라이언트 ID)
│   │   ├── data/
│   │   │   ├── token.json          (Google 인증 토큰)
│   │   │   └── mapping.db          (UUID 매핑 DB)
│   │   └── logs/
│   │       └── sync.log            (동기화 로그)
│   └── Info.plist                   (앱 정보)

~/.reminders-to-gcal-prefs.json      (사용자 환경설정)
~/.reminders-to-gcal.lock            (단일 인스턴스 락 파일)
```

---

## 🚀 사용 방법

### 첫 실행
1. Applications 폴더에서 앱 더블클릭
2. 보안 경고 시 "확인 없이 열기"
3. 메뉴바에 "R→GCal" 아이콘 나타남

### 첫 동기화
1. 메뉴바 아이콘 클릭 → "Sync Now"
2. 미리알림 권한 요청 → 허용
3. 브라우저 열림 → Google 로그인
4. 권한 허용 → "인증 완료"
5. 동기화 시작!

### 환경설정
1. 메뉴바 아이콘 클릭 → "Preferences..."
2. 자동 동기화 간격 입력 (분 단위)
3. "Save" 클릭
4. 알림으로 확인

---

## 📱 멀티 디바이스 지원

### iPhone/iPad
- iCloud로 자동 동기화
- iPhone에서 미리알림 추가 → 맥에서 자동 감지
- 추가 설정 불필요

### 다른 Mac
- DMG 파일로 설치
- credentials.json 자동 포함 (DMG에 내장)
- OAuth 인증만 1회 필요
- iCloud Drive로 설정 공유 가능

---

## 🔧 문제 해결

### Q: 동기화가 안 돼요
**확인 사항:**
1. 인터넷 연결 확인
2. 미리알림 권한 확인
3. Google 인증 확인
4. 로그 확인 (View Logs)

**해결 방법:**
- 메뉴에서 "Sync Now" → 에러 메시지 확인
- "Re-authenticate" 옵션 선택

### Q: 앱이 실행 안 돼요
**해결:**
```bash
xattr -cr /Applications/Reminders\ to\ GCal.app
```

### Q: 중복 이벤트가 생성돼요
**원인:** UUID 매핑 DB 손상
**해결:**
```bash
rm /Applications/Reminders\ to\ GCal.app/Contents/Resources/data/mapping.db
```

---

## 📊 동기화 규칙

### 생성 (Create)
- 새로운 미리알림 감지
- Google Calendar에 이벤트 생성
- UUID 매핑 DB에 기록

### 업데이트 (Update)
- 기존 미리알림 변경 감지 (checksum 비교)
- Google Calendar 이벤트 업데이트
- 변경 사항: 제목, 노트, 날짜, 우선순위, 완료 상태, 위치

### 삭제 (Delete)
- 미리알림 삭제 감지
- Google Calendar 이벤트 삭제
- UUID 매핑 DB에서 제거

### 완료 처리
- 환경설정에서 동기화 여부 설정 가능
- 완료된 미리알림은 strikethrough 표시

---

## 🎯 향후 계획 (Future)

### 예정 기능
- [ ] 키보드 단축키
- [ ] 앱 내 로그 뷰어
- [ ] 업데이트 자동 확인
- [ ] Code Signing (Apple Developer 인증서)
- [ ] 양방향 동기화 (Google Calendar → Reminders)
- [ ] 특정 미리알림 리스트 선택 동기화
- [ ] 시각적 설정 창 (GUI Preferences)

---

## 📝 버전 히스토리

### Version 2.0 (2025-11-10)
- ✅ Preferences 창 추가
- ✅ 자동 동기화 타이머
- ✅ 로그인 시 자동 시작
- ✅ Help 메뉴
- ✅ 상태 표시 개선
- ✅ 에러 복구 옵션
- ✅ 단일 인스턴스 실행
- ✅ DMG 인스톨러

### Version 1.0 (2025-11-09)
- ✅ 기본 동기화 기능
- ✅ 메뉴바 앱
- ✅ Google OAuth 인증
- ✅ UUID 매핑
- ✅ 위치 동기화
- ✅ 타임존 처리 (Asia/Seoul)

---

**개발자**: Claude Code
**라이선스**: MIT
**저작권**: © 2025
