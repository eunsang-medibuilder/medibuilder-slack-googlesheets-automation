#!/usr/bin/env python3
"""
Excel 파일 연동 테스트 스크립트
"""

import os
from dotenv import load_dotenv
from services.hybrid_sheets_service import HybridSheetsService

def test_excel_integration():
    """Excel 파일 연동 테스트"""
    
    load_dotenv()
    
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
    file_id = os.getenv('GOOGLE_SPREADSHEET_ID')
    sheet_name = os.getenv('TARGET_SHEET_NAME', '개발팀')
    
    print("🧪 Excel 파일 연동 테스트 시작")
    print(f"📄 파일 ID: {file_id}")
    print(f"📋 시트명: {sheet_name}")
    
    try:
        # 서비스 초기화
        excel_service = HybridSheetsService(credentials_path, file_id)
        
        # 테스트 데이터
        test_data = {
            'I': '1.50%',
            'L': '3.25%', 
            'N': '95.25%',
            'O': '- 2025 9월 3주차(테스트)'
        }
        
        print("📝 테스트 데이터 입력 중...")
        row_number = excel_service.update_with_temp_conversion(sheet_name, test_data)
        
        print(f"✅ 테스트 성공! {row_number}행에 데이터가 입력되었습니다.")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_excel_integration()
