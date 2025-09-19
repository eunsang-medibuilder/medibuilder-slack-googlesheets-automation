# 🔧 Google Sheets API 문제 해결 가이드

## 🚨 발견된 문제

현재 스프레드시트 ID `14n_l2K4Koxtf097RJFkv1VVSASW_t8Mg`가 가리키는 파일은:
- **파일명**: 2025년 메디빌더 HQ_주간 업무 비중 기록.xlsx
- **파일 타입**: Excel 파일 (.xlsx)
- **문제**: Google Sheets가 아니므로 Google Sheets API로 접근할 수 없음

## 💡 해결 방법

### 방법 1: Excel 파일을 Google Sheets로 변환 (권장)

1. **Google Drive에서 파일 열기**
   - Google Drive에서 해당 Excel 파일을 찾습니다
   - 파일을 더블클릭하여 엽니다

2. **Google Sheets로 변환**
   - 파일이 열리면 상단에 "Google Sheets로 저장" 버튼이 나타납니다
   - 또는 `파일 > Google Sheets로 저장` 메뉴를 선택합니다

3. **새로운 스프레드시트 ID 확인**
   - 변환된 Google Sheets의 URL에서 새로운 ID를 복사합니다
   - URL 형식: `https://docs.google.com/spreadsheets/d/[새로운_ID]/edit`

4. **환경변수 업데이트**
   ```bash
   # .env 파일에서 GOOGLE_SPREADSHEET_ID를 새로운 ID로 변경
   GOOGLE_SPREADSHEET_ID=새로운_스프레드시트_ID
   ```

### 방법 2: 서비스 계정 권한 부여

변환된 Google Sheets에 서비스 계정 권한을 부여해야 합니다:

1. **Google Sheets 열기**
2. **공유 버튼 클릭**
3. **서비스 계정 이메일 추가**:
   ```
   medibuilder-google-sheets-api@gen-lang-client-0829987926.iam.gserviceaccount.com
   ```
4. **편집자 권한 부여**

### 방법 3: 자동 변환 스크립트 (고급)

```python
# convert_to_sheets.py
from google.oauth2 import service_account
from googleapiclient.discovery import build

def convert_excel_to_sheets(file_id, credentials_path):
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    drive_service = build('drive', 'v3', credentials=creds)
    
    # 파일 복사 (Google Sheets 형식으로)
    copied_file = drive_service.files().copy(
        fileId=file_id,
        body={
            'name': '2025년 메디빌더 HQ_주간 업무 비중 기록 (Google Sheets)',
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
    ).execute()
    
    print(f"새로운 Google Sheets ID: {copied_file['id']}")
    return copied_file['id']
```

## ✅ 해결 후 확인

변환 완료 후 다시 점검 스크립트를 실행하세요:

```bash
python3 api_checker.py
```

## 🎯 예상 결과

성공적으로 변환되면 다음과 같은 결과를 볼 수 있습니다:

```
3️⃣ 파일 타입 확인...
   ✅ 파일명: 2025년 메디빌더 HQ_주간 업무 비중 기록
   📄 파일 타입: application/vnd.google-apps.spreadsheet
   ✅ 서비스 계정 권한: editor
```

## 🚀 다음 단계

1. Excel 파일을 Google Sheets로 변환
2. 서비스 계정에 편집 권한 부여  
3. .env 파일의 스프레드시트 ID 업데이트
4. `python3 api_checker.py` 재실행
5. 모든 테스트 통과 후 `python3 main.py` 실행 가능
