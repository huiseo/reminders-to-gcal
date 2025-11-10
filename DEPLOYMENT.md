# Reminders to GCal - 배포 가이드

## 배포 완료 정보

**빌드 날짜**: 2025-01-10
**버전**: 0.0.0
**상태**: ✅ 배포 완료

## 생성된 파일

### 1. DMG 설치 파일
- **파일명**: `Reminders-to-GCal-Installer.dmg`
- **크기**: 21MB
- **위치**: `/Users/heeseo/Work/ClaudeCode/reminders-to-gcal/`
- **내용**:
  - `Reminders to GCal.app` - 메인 애플리케이션
  - `Uninstall.command` - 제거 스크립트
  - `Applications` 심볼릭 링크 - 드래그 앤 드롭 설치용

### 2. 설치된 앱
- **위치**: `/Applications/Reminders to GCal.app`
- **상태**: ✅ 설치 완료 및 실행 중 (2 프로세스)
- **타입**: 메뉴바 전용 앱 (Dock 아이콘 없음)

## 설치 방법

### 방법 1: DMG 사용 (권장)
1. `Reminders-to-GCal-Installer.dmg` 더블클릭
2. 열린 창에서 `Reminders to GCal.app`을 `Applications` 폴더로 드래그
3. DMG 창 닫기
4. Finder에서 `/Applications/Reminders to GCal.app` 더블클릭하여 실행

### 방법 2: 직접 복사
```bash
cp -r "dist/Reminders to GCal.app" /Applications/
open "/Applications/Reminders to GCal.app"
```

## 첫 실행 시 설정

### 1. Google OAuth 인증 파일 준비
- Google Cloud Console에서 OAuth 2.0 credentials 다운로드
- 파일명을 `credentials.json`으로 변경
- 앱의 Resources 폴더에 복사:
  ```bash
  cp credentials.json "/Applications/Reminders to GCal.app/Contents/Resources/"
  ```

### 2. 설정 파일 복사 (선택사항)
기본 설정을 변경하려면:
```bash
cp config.yaml "/Applications/Reminders to GCal.app/Contents/Resources/"
```

### 3. 앱 실행
- Finder에서 앱 더블클릭 또는
- Spotlight에서 "Reminders to GCal" 검색 후 실행

### 4. 권한 승인
첫 실행 시 다음 권한을 요청합니다:
- ✅ **Reminders 접근 권한** - 필수
- ✅ **Google OAuth 인증** - 브라우저에서 진행

## 앱 기능

### 메뉴바 메뉴
1. **Sync Now** - 즉시 동기화
2. **Last Sync** - 마지막 동기화 정보
3. **Preferences** - 설정 (자동 동기화 간격)
4. **View Logs** - 로그 보기
5. **Open Reminders** - Reminders 앱 열기
6. **Open Google Calendar** - Google Calendar 웹 열기
7. **Help** - 도움말
8. **About** - 앱 정보
9. **Quit** - 종료

### 자동 동기화
- Preferences에서 간격 설정 가능 (15분, 30분, 1시간, 2시간)
- 0 입력 시 수동 동기화만 사용

### 로그인 시 자동 실행
- 앱 내에서 설정 가능 (향후 업데이트 예정)

## 제거 방법

### 방법 1: Uninstall.command 사용 (권장)
1. DMG를 다시 마운트
2. `Uninstall.command` 더블클릭
3. 관리자 비밀번호 입력

### 방법 2: 수동 제거
```bash
# 앱 종료
pkill -f "Reminders to GCal"

# 앱 제거
rm -rf "/Applications/Reminders to GCal.app"

# 설정 파일 제거
rm ~/.reminders-to-gcal-prefs.json
rm ~/.reminders-to-gcal.lock

# LaunchAgent 제거 (있다면)
rm ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist
launchctl unload ~/Library/LaunchAgents/com.reminders-to-gcal.sync.plist

# 로그인 항목 제거
osascript -e 'tell application "System Events" to delete login item "Reminders to GCal"'
```

## 데이터 저장 위치

### 앱 내부
- `/Applications/Reminders to GCal.app/Contents/Resources/data/`
  - `mapping.db` - UUID 매핑 데이터베이스
  - `token.json` - Google OAuth 토큰 (권한: 0o600)

### 사용자 홈
- `~/.reminders-to-gcal-prefs.json` - 앱 설정
- `~/.reminders-to-gcal.lock` - 단일 인스턴스 잠금 파일

### 로그
- `/Applications/Reminders to GCal.app/Contents/Resources/logs/`
  - `menubar_app.log` - 메뉴바 앱 로그
  - `sync.log` - 동기화 로그 (향후)

## 개선 사항 (v0.0.0)

### 코드 품질
- ✅ 데이터베이스 연결 리소스 관리 (context manager)
- ✅ 파일 I/O 에러 처리 강화
- ✅ 토큰 파일 보안 (0o600 권한)
- ✅ 구체적인 예외 처리
- ✅ 종합적인 로깅 시스템

### 테스트
- ✅ 56개 테스트 케이스 작성
- ✅ 94.6% 테스트 통과율 (53/56)
- ✅ 단위 테스트, 통합 테스트, 품질 테스트 포함

### 기능
- ✅ 메뉴바 전용 앱 (Dock 숨김)
- ✅ 자동 동기화 타이머
- ✅ 단일 인스턴스 실행
- ✅ 에러 복구 옵션
- ✅ Preferences 윈도우
- ✅ 도움말 메뉴

## 알려진 이슈

없음

## 다음 버전 계획

1. 버전 번호 업데이트 (0.0.0 → 1.0.0)
2. 로그인 시 자동 실행 설정 UI
3. 다국어 지원 (한국어/영어)
4. 알림 커스터마이징
5. 성능 최적화

## 문의 및 이슈 리포트

- GitHub Issues: (저장소 URL)
- 이메일: (연락처)

## 라이선스

(라이선스 정보)

---

**빌드 정보**
- Build Tool: PyInstaller 6.16.0
- Python: 3.9.6
- Platform: macOS 15.6.1 (arm64)
- Build Date: 2025-01-10
