# Reminders to Google Calendar

Mac/iPhone Reminders를 Google Calendar와 자동으로 동기화하는 macOS 메뉴바 앱입니다.

![Version](https://img.shields.io/badge/version-0.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 주요 기능

- ✅ **양방향 동기화**: Mac/iPhone Reminders → Google Calendar
- ✅ **자동 동기화**: 설정 가능한 간격으로 자동 실행 (15분, 30분, 1시간, 2시간)
- ✅ **메뉴바 통합**: 가볍고 편리한 메뉴바 앱
- ✅ **우선순위 색상**: Reminders 우선순위를 Google Calendar 색상으로 매핑
- ✅ **위치 정보**: Reminders의 위치 정보도 동기화
- ✅ **완료 처리**: 완료된 항목 자동 삭제 또는 유지
- ✅ **중복 방지**: UUID 기반 매핑으로 중복 생성 방지
- ✅ **에러 복구**: 동기화 실패 시 재시도 및 재인증 옵션

## 스크린샷

(추후 추가)

## 시스템 요구사항

- macOS 10.15 (Catalina) 이상
- Python 3.9 이상 (개발용)
- Google Account
- Apple ID (iCloud 동기화용)

## 설치 방법

### 방법 1: DMG 설치 (권장)

1. [Releases](https://github.com/heeseo/reminders-to-gcal/releases)에서 최신 DMG 다운로드
2. DMG 파일을 열고 `Reminders to GCal.app`을 `Applications` 폴더로 드래그
3. 앱 실행

### 방법 2: 소스에서 빌드

```bash
# 저장소 클론
git clone https://github.com/heeseo/reminders-to-gcal.git
cd reminders-to-gcal

# 의존성 설치
pip3 install -r requirements.txt

# 앱 빌드
./build_app.sh

# 설치
cp -r "dist/Reminders to GCal.app" /Applications/
```

## 초기 설정

### 1. Google OAuth 인증 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Calendar API 활성화
4. OAuth 2.0 클라이언트 ID 생성 (Desktop app)
5. `credentials.json` 다운로드
6. 파일을 앱의 Resources 폴더에 복사:
   ```bash
   cp credentials.json "/Applications/Reminders to GCal.app/Contents/Resources/"
   ```

### 2. 첫 실행

1. Finder에서 `Reminders to GCal.app` 더블클릭
2. Reminders 접근 권한 승인
3. 브라우저에서 Google OAuth 인증 완료
4. 메뉴바에서 R→GCal 아이콘 확인

## 사용 방법

### 메뉴바 메뉴

- **Sync Now**: 즉시 동기화 실행
- **Last Sync**: 마지막 동기화 정보 표시
- **Preferences**: 자동 동기화 간격 설정
- **View Logs**: 동기화 로그 확인
- **Open Reminders**: Reminders 앱 열기
- **Open Google Calendar**: Google Calendar 웹 열기
- **Help**: 도움말 및 GitHub 이슈 페이지
- **About**: 앱 정보
- **Quit**: 앱 종료

### 설정 변경

`config.yaml` 파일을 수정하여 다양한 설정을 변경할 수 있습니다:

```yaml
reminders:
  sync_lists: []  # 특정 목록만 동기화 (비워두면 전체)
  skip_completed_older_than_days: 30  # 오래된 완료 항목 제외

sync:
  completed_action: delete  # 완료 시 동작: delete 또는 keep

google_calendar:
  calendar_id: primary  # 대상 캘린더 ID
  priority_colors:
    high: "11"    # 빨강
    medium: "5"   # 노랑
    low: "7"      # 파랑
```

## 아키텍처

```
reminders-to-gcal/
├── src/
│   ├── auth.py              # Google OAuth 인증
│   ├── reminders_reader.py  # Mac Reminders 읽기 (EventKit)
│   ├── gcal_writer.py       # Google Calendar 쓰기
│   └── sync_engine.py       # 동기화 로직 및 DB
├── tests/                   # 테스트 코드 (56개)
├── menubar_app.py          # 메뉴바 앱 (rumps)
├── config.yaml             # 설정 파일
├── build_app.sh            # 빌드 스크립트
└── Uninstall.command       # 제거 스크립트
```

## 개발

### 개발 환경 설정

```bash
# 의존성 설치
pip3 install -r requirements.txt

# 테스트 실행
python3 -m unittest discover -s tests -v

# 앱 실행 (개발 모드)
python3 menubar_app.py
```

### 테스트

- **총 56개 테스트**
- **94.6% 통과율** (53/56 통과)
- 단위 테스트, 통합 테스트, 품질 테스트 포함

```bash
# 전체 테스트 실행
python3 -m unittest discover -s tests

# 특정 테스트 실행
python3 -m unittest tests.test_sync_engine
python3 -m unittest tests.test_quality
```

### 빌드

```bash
# 앱 빌드
./build_app.sh

# DMG 생성
hdiutil create -volname "Reminders to GCal" \
  -srcfolder /tmp/dmg_build \
  -ov -format UDZO \
  "Reminders-to-GCal-Installer.dmg"
```

## 데이터 및 프라이버시

### 저장되는 데이터

- **로컬 데이터베이스** (`mapping.db`): UUID 매핑만 저장
- **OAuth 토큰** (`token.json`): 권한 0o600으로 보호
- **설정 파일**: 사용자 환경설정

### 데이터 전송

- Google Calendar API를 통해서만 데이터 전송
- 모든 통신은 HTTPS로 암호화
- 제3자 서버로 데이터 전송 없음

## 문제 해결

### 앱이 실행되지 않을 때

```bash
# 로그 확인
tail -f "/Applications/Reminders to GCal.app/Contents/Resources/logs/menubar_app.log"

# 권한 확인
ls -la "/Applications/Reminders to GCal.app/Contents/Resources/credentials.json"

# 잠금 파일 제거
rm ~/.reminders-to-gcal.lock
```

### 동기화가 안 될 때

1. **Preferences**에서 자동 동기화 간격 확인
2. **View Logs**에서 에러 메시지 확인
3. Google OAuth 토큰 재설정:
   ```bash
   rm "/Applications/Reminders to GCal.app/Contents/Resources/data/token.json"
   ```
4. 앱 재시작 후 재인증

## 제거

### DMG의 Uninstall.command 사용

1. DMG를 다시 마운트
2. `Uninstall.command` 더블클릭
3. 관리자 비밀번호 입력

### 수동 제거

```bash
# 앱 종료
pkill -f "Reminders to GCal"

# 모든 파일 제거
rm -rf "/Applications/Reminders to GCal.app"
rm ~/.reminders-to-gcal-prefs.json
rm ~/.reminders-to-gcal.lock
```

## 기여

Pull Request를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일 참조

## 로드맵

- [ ] v1.0.0 - 첫 정식 릴리스
- [ ] 로그인 시 자동 실행 UI
- [ ] 다국어 지원 (한국어/영어)
- [ ] 양방향 동기화 (Google Calendar → Reminders)
- [ ] 선택적 목록 동기화 UI
- [ ] 성능 최적화 (대용량 데이터)

## 참고 자료

- [Google Calendar API Documentation](https://developers.google.com/calendar)
- [PyObjC - EventKit](https://pyobjc.readthedocs.io/)
- [rumps - macOS menubar apps](https://github.com/jaredks/rumps)

## 문의

- **Issues**: [GitHub Issues](https://github.com/heeseo/reminders-to-gcal/issues)
- **Email**: hui.seo@gmail.com

---

**Made with ❤️ for productivity**
