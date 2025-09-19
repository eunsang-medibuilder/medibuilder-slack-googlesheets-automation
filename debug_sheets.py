#!/usr/bin/env python3
"""
Google Sheets 연결 디버깅 스크립트
"""

import gspread
from google.oauth2.service_account import Credentials
from config import Config

def test_sheets_connection():
    """Google Sheets 연결 테스트"""
    try:
        Config.validate()
        
        print("🔍 Google Sheets 연결 테스트 시작")
        print(f"인증 파일: {Config.GOOGLE_SHEETS_CREDENTIALS_PATH}")
        print(f"스프레드시트 ID: {Config.GOOGLE_SPREADSHEET_ID}")
        print(f"시트 이름: {Config.TARGET_SHEET_NAME}")
        
        # 인증 설정
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH, 
            scopes=scope
        )
        
        client = gspread.authorize(creds)
        print("✅ 인증 성공")
        
        # 스프레드시트 열기 시도
        try:
            spreadsheet = client.open_by_key(Config.GOOGLE_SPREADSHEET_ID)
            print(f"✅ 스프레드시트 열기 성공: {spreadsheet.title}")
        except gspread.SpreadsheetNotFound:
            print("❌ 스프레드시트를 찾을 수 없습니다")
            print("   → 스프레드시트 ID가 올바른지 확인하세요")
            print("   → 서비스 계정에 스프레드시트 접근 권한이 있는지 확인하세요")
            return False
        
        # 워크시트 열기 시도
        try:
            worksheet = spreadsheet.worksheet(Config.TARGET_SHEET_NAME)
            print(f"✅ 워크시트 열기 성공: {worksheet.title}")
        except gspread.WorksheetNotFound:
            print(f"❌ 워크시트 '{Config.TARGET_SHEET_NAME}'를 찾을 수 없습니다")
            print("   → 사용 가능한 워크시트:")
            for ws in spreadsheet.worksheets():
                print(f"     - {ws.title}")
            return False
        
        # 간단한 읽기 테스트
        try:
            all_values = worksheet.get_all_values()
            print(f"✅ 데이터 읽기 성공: {len(all_values)}행")
        except Exception as e:
            print(f"❌ 데이터 읽기 실패: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 일반 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Google Sheets 연결 디버깅 시작")
    print("=" * 50)
    
    if test_sheets_connection():
        print("\n✅ 모든 테스트 통과!")
    else:
        print("\n❌ 테스트 실패!")
