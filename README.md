# Slack to Google Sheets Automation

Slack 봇 메시지의 스레드 댓글을 분석하여 Google Spreadsheet에 자동으로 데이터를 입력하는 애플리케이션입니다.

## 기능

- Slack 스레드 댓글 자동 감지 및 분석
- Google Gemini AI를 사용한 텍스트 데이터 추출
- Google Sheets 자동 업데이트
- 에러 발생 시 Slack 알림

## 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 입력하세요
```

### 2. 필수 환경변수

```
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id
TARGET_SHEET_NAME=your-sheet-name
GEMINI_API_KEY=your-gemini-api-key
```

### 3. 실행

```bash
# 기본 실행
python main.py

# 특정 채널과 스레드 지정
python main.py --channel-id C1234567890 --thread-ts 1234567890.123456
```

## 테스트

```bash
# 모든 테스트 실행
python -m pytest

# 특정 테스트 실행
python -m pytest tests/test_slack_service.py -v
```

## 프로젝트 구조

```
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 관리
├── services/              # 핵심 서비스
│   ├── slack_service.py   # Slack API 처리
│   ├── sheets_service.py  # Google Sheets API 처리
│   └── gemini_service.py  # Gemini AI 처리
├── models/                # 데이터 모델
│   └── spreadsheet_row.py # 스프레드시트 행 모델
├── tests/                 # 테스트 파일
└── utils/                 # 유틸리티 함수
```
