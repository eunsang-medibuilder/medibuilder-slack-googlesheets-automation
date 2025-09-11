# Slack to Google Sheets 자동화 시스템

Slack 주간업무 현황 메시지를 분석하여 Google Spreadsheet에 자동으로 데이터를 입력하는 애플리케이션입니다.

## 🚀 주요 기능

- **Slack 메시지 파싱**: 주간업무 현황 메시지에서 완료 작업 시간 데이터 추출
- **비율 자동 계산**: 온리프+심플치과 합산하여 총합 대비 비율 계산
- **Google Sheets 자동 업데이트**: 지정된 열에 데이터 자동 입력
- **에러 처리**: 파싱 실패 시 기본값(00.00%) 적용 및 Slack 알림

## 📊 데이터 매핑

| 열 | 내용 | 예시 |
|---|---|---|
| I열 | 온리프 + 심플치과 비율 | 1.92% |
| L열 | 르샤인 비율 | 4.81% |
| N열 | 오블리브 비율 | 93.27% |
| O열 | `- 년도 주차(이름)` + 전체 메시지 | `- 2025 9월 1주차(이은상)` |

## 📝 지원하는 메시지 형식

```
2025년 9월 1주차 주간업무 현황
기간 : 25. 9. 1 ~ 25. 9. 5

금주 완료 작업 소요시간 합계(시간)
온리프 : 1
르샤인 : 2.5
오블리브 : 48.5
심플 : 0

총합 : 52 시간
...
```

## 🛠️ 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 입력하세요
```

### 3. 필수 환경변수

```
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SPREADSHEET_ID=your-spreadsheet-id
TARGET_SHEET_NAME=your-sheet-name
```

## 🚀 사용법

### 기본 실행
```bash
python main.py --channel-id C1234567890 --thread-ts 1234567890.123456
```

### 작성자 이름 지정
```bash
python main.py --channel-id C1234567890 --thread-ts 1234567890.123456 --author-name "홍길동"
```

## 🧪 테스트

```bash
# 모든 테스트 실행
python -m pytest

# 특정 테스트 실행
python -m pytest tests/test_message_parser.py -v
```

## 📁 프로젝트 구조

```
├── main.py                 # 메인 실행 파일
├── config.py              # 설정 관리
├── services/              # 핵심 서비스
│   ├── slack_service.py   # Slack API 처리
│   ├── sheets_service.py  # Google Sheets API 처리
│   └── message_parser.py  # 메시지 파싱 로직
├── models/                # 데이터 모델
│   └── spreadsheet_row.py # 스프레드시트 행 모델
├── tests/                 # 테스트 파일
└── requirements.txt       # 의존성 목록
```

## 🔧 비율 계산 로직

1. **온리프 + 심플치과**: 두 병원의 시간을 합산하여 총합 대비 비율 계산
2. **르샤인**: 개별 시간의 총합 대비 비율 계산  
3. **오블리브**: 개별 시간의 총합 대비 비율 계산
4. **파싱 실패 시**: 모든 비율을 `00.00%`로 설정
