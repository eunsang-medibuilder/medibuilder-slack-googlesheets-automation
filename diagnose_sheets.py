#!/usr/bin/env python3
"""
Google Sheets 상세 진단 스크립트
"""

import gspread
from google.oauth2.service_account import Credentials
from config import Config

def diagnose_sheets():
    """Google Sheets 상세 진단"""
    try:
        Config.validate()
        
        print("🔍 Google Sheets 상세 진단 시작")
        print(f"스프레드시트 ID: {Config.GOOGLE_SPREADSHEET_ID}")
        
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
        
        # 스프레드시트 정보 확인
        try:
            spreadsheet = client.open_by_key(Config.GOOGLE_SPREADSHEET_ID)
            print(f"✅ 스프레드시트: {spreadsheet.title}")
            print(f"   URL: {spreadsheet.url}")
            print(f"   ID: {spreadsheet.id}")
            
            # 워크시트 목록
            print("\n📋 사용 가능한 워크시트:")
            for i, ws in enumerate(spreadsheet.worksheets(), 1):
                print(f"   {i}. {ws.title} (ID: {ws.id})")
            
            # 대상 워크시트 확인
            if Config.TARGET_SHEET_NAME:
                try:
                    worksheet = spreadsheet.worksheet(Config.TARGET_SHEET_NAME)
                    print(f"\n✅ 대상 워크시트 '{Config.TARGET_SHEET_NAME}' 발견")
                    print(f"   행 수: {worksheet.row_count}")
                    print(f"   열 수: {worksheet.col_count}")
                    
                    # 첫 번째 행 읽기 시도
                    try:
                        first_row = worksheet.row_values(1)
                        print(f"   첫 번째 행: {first_row[:5]}...")  # 처음 5개만 표시
                    except Exception as e:
                        print(f"   ❌ 첫 번째 행 읽기 실패: {e}")
                        
                except gspread.WorksheetNotFound:
                    print(f"\n❌ 워크시트 '{Config.TARGET_SHEET_NAME}' 없음")
            
        except Exception as e:
            print(f"❌ 스프레드시트 접근 실패: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 진단 실패: {e}")
        return False

if __name__ == "__main__":
    diagnose_sheets()
