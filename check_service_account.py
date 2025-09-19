#!/usr/bin/env python3
"""
서비스 계정 정보 확인
"""

import json
from config import Config

def check_service_account():
    """서비스 계정 정보 확인"""
    try:
        with open(Config.GOOGLE_SHEETS_CREDENTIALS_PATH, 'r') as f:
            creds = json.load(f)
        
        print("🔍 서비스 계정 정보:")
        print(f"   이메일: {creds.get('client_email')}")
        print(f"   프로젝트 ID: {creds.get('project_id')}")
        print(f"   클라이언트 ID: {creds.get('client_id')}")
        
        print("\n📝 다음 단계:")
        print("1. Google Sheets에서 스프레드시트를 열어주세요")
        print("2. '공유' 버튼을 클릭하세요")
        print(f"3. 다음 이메일을 편집자로 추가하세요: {creds.get('client_email')}")
        
    except Exception as e:
        print(f"❌ 서비스 계정 정보 확인 실패: {e}")

if __name__ == "__main__":
    check_service_account()
