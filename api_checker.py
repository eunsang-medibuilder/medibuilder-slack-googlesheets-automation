#!/usr/bin/env python3
"""
Google Sheets API 연결 상태 점검 스크립트
기존 프로젝트의 환경설정을 활용하여 API 접근성을 진단합니다.
"""

import os
import json
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

class GoogleAPIChecker:
    def __init__(self):
        # 환경변수 로드
        load_dotenv()
        
        self.credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        self.spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.sheet_name = os.getenv('TARGET_SHEET_NAME', 'Sheet1')
        
    def check_env_variables(self):
        """환경변수 설정 확인"""
        print("1️⃣ 환경변수 설정 확인...")
        
        missing = []
        if not self.credentials_path:
            missing.append('GOOGLE_SHEETS_CREDENTIALS_PATH')
        if not self.spreadsheet_id:
            missing.append('GOOGLE_SPREADSHEET_ID')
            
        if missing:
            print(f"   ❌ 누락된 환경변수: {', '.join(missing)}")
            print("   💡 .env 파일을 확인하세요")
            return False
            
        print(f"   ✅ 자격증명 파일: {self.credentials_path}")
        print(f"   ✅ 스프레드시트 ID: {self.spreadsheet_id}")
        print(f"   ✅ 대상 시트명: {self.sheet_name}")
        return True
    
    def check_credentials_file(self):
        """자격증명 파일 확인"""
        print("\n2️⃣ 자격증명 파일 확인...")
        
        if not os.path.exists(self.credentials_path):
            print(f"   ❌ 파일이 존재하지 않습니다: {self.credentials_path}")
            return False
            
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            
            required_fields = ['client_email', 'project_id', 'private_key']
            missing_fields = [field for field in required_fields if not cred_data.get(field)]
            
            if missing_fields:
                print(f"   ❌ 필수 필드 누락: {', '.join(missing_fields)}")
                return False
                
            print(f"   ✅ 서비스 계정: {cred_data['client_email']}")
            print(f"   ✅ 프로젝트 ID: {cred_data['project_id']}")
            return True
            
        except json.JSONDecodeError:
            print("   ❌ JSON 형식이 올바르지 않습니다")
            return False
        except Exception as e:
            print(f"   ❌ 파일 읽기 실패: {e}")
            return False
    
    def check_file_type(self):
        """파일 타입 확인"""
        print("\n3️⃣ 파일 타입 확인...")
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            drive_service = build('drive', 'v3', credentials=creds)
            
            file_info = drive_service.files().get(
                fileId=self.spreadsheet_id,
                fields='id, name, mimeType, permissions'
            ).execute()
            
            print(f"   ✅ 파일명: {file_info.get('name')}")
            print(f"   📄 파일 타입: {file_info.get('mimeType')}")
            
            # Google Sheets 타입 확인
            if file_info.get('mimeType') != 'application/vnd.google-apps.spreadsheet':
                print("   ❌ 이 파일은 Google Sheets가 아닙니다!")
                print("   💡 Google Sheets로 변환하거나 올바른 파일 ID를 사용하세요")
                return False
            
            # 권한 확인
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            service_email = cred_data['client_email']
            
            has_permission = False
            for perm in file_info.get('permissions', []):
                if perm.get('emailAddress') == service_email:
                    print(f"   ✅ 서비스 계정 권한: {perm.get('role')}")
                    has_permission = True
                    break
            
            if not has_permission:
                print(f"   ❌ 서비스 계정 권한 없음!")
                print(f"   💡 Google Sheets에서 {service_email}에게 편집 권한을 부여하세요")
                return False
            
            return True
            
        except Exception as e:
            print(f"   ❌ 파일 확인 실패: {e}")
            if "404" in str(e):
                print("   💡 파일을 찾을 수 없습니다. 스프레드시트 ID를 확인하세요")
            elif "403" in str(e):
                print("   💡 Drive API 권한이 필요합니다")
            return False

    def check_sheets_connection(self):
        """Google Sheets 연결 테스트"""
        print("\n4️⃣ Google Sheets 연결 테스트...")
        
        try:
            # gspread를 사용한 연결 테스트
            gc = gspread.service_account(filename=self.credentials_path)
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            
            print(f"   ✅ 스프레드시트 접근 성공: '{spreadsheet.title}'")
            
            # 대상 워크시트 확인
            try:
                worksheet = spreadsheet.worksheet(self.sheet_name)
                print(f"   ✅ 워크시트 접근 성공: '{worksheet.title}'")
            except gspread.WorksheetNotFound:
                print(f"   ⚠️ 워크시트 '{self.sheet_name}'를 찾을 수 없습니다")
                print(f"   💡 사용 가능한 시트: {[ws.title for ws in spreadsheet.worksheets()]}")
                worksheet = spreadsheet.sheet1
                print(f"   ✅ 기본 시트 사용: '{worksheet.title}'")
            
            return worksheet
            
        except gspread.SpreadsheetNotFound:
            print("   ❌ 스프레드시트를 찾을 수 없습니다")
            print("   💡 스프레드시트 ID가 올바른지 확인하세요")
            return None
        except Exception as e:
            print(f"   ❌ 연결 실패: {e}")
            if "403" in str(e):
                print("   💡 권한 문제: 서비스 계정에 스프레드시트 편집 권한을 부여하세요")
            elif "400" in str(e) and "not supported" in str(e):
                print("   💡 파일이 Google Sheets 형식이 아닐 수 있습니다")
            return None
    
    def test_read_write_operations(self, worksheet):
        """읽기/쓰기 작업 테스트"""
        print("\n5️⃣ 읽기/쓰기 작업 테스트...")
        
        try:
            # 읽기 테스트 - 프로젝트에서 사용하는 열들 확인
            test_ranges = ['I1', 'L1', 'N1', 'O1']  # 프로젝트에서 사용하는 열들
            
            for cell_range in test_ranges:
                try:
                    value = worksheet.acell(cell_range).value
                    print(f"   ✅ {cell_range} 읽기 성공: '{value or '(빈 셀)'}'")
                except Exception as e:
                    print(f"   ⚠️ {cell_range} 읽기 실패: {e}")
            
            # 쓰기 테스트 - 임시 셀에 테스트 데이터 작성
            test_cell = 'Z1'  # 임시 테스트용 셀
            test_value = 'API 테스트 완료'
            
            worksheet.update(test_cell, test_value)
            print(f"   ✅ {test_cell} 쓰기 성공")
            
            # 쓰기 확인
            written_value = worksheet.acell(test_cell).value
            if written_value == test_value:
                print(f"   ✅ 쓰기 검증 성공")
            else:
                print(f"   ⚠️ 쓰기 검증 실패: 예상 '{test_value}', 실제 '{written_value}'")
            
            # 테스트 데이터 정리
            worksheet.update(test_cell, '')
            print(f"   ✅ 테스트 데이터 정리 완료")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 읽기/쓰기 테스트 실패: {e}")
            return False
    
    def check_project_specific_setup(self, worksheet):
        """프로젝트별 설정 확인"""
        print("\n6️⃣ 프로젝트별 설정 확인...")
        
        # 프로젝트에서 사용하는 열 구조 확인
        target_columns = {
            'I': '온리프+심플치과 비율',
            'L': '르샤인 비율', 
            'N': '오블리브 비율',
            'O': '메모 (년도 주차 + 작성자)'
        }
        
        print("   📊 대상 열 구조:")
        for col, desc in target_columns.items():
            print(f"      {col}열: {desc}")
        
        # 헤더 행 확인 (1행이 헤더인지 확인)
        try:
            header_range = 'A1:O1'
            headers = worksheet.get(header_range)[0] if worksheet.get(header_range) else []
            
            if headers:
                print(f"   ✅ 헤더 행 감지됨 (총 {len(headers)}개 열)")
                for i, header in enumerate(headers[:15], 1):  # A~O열까지만 표시
                    if header:
                        col_letter = chr(64 + i)  # A=65, B=66, ...
                        print(f"      {col_letter}열: '{header}'")
            else:
                print("   ⚠️ 헤더 행이 비어있거나 감지되지 않음")
                
        except Exception as e:
            print(f"   ⚠️ 헤더 확인 실패: {e}")
        
        return True
    
    def run_diagnosis(self):
        """전체 진단 실행"""
        print("🔍 Google Sheets API 연결 진단 시작")
        print("=" * 50)
        
        # 단계별 진단
        if not self.check_env_variables():
            return False
            
        if not self.check_credentials_file():
            return False
            
        if not self.check_file_type():
            return False
            
        worksheet = self.check_sheets_connection()
        if not worksheet:
            return False
            
        if not self.test_read_write_operations(worksheet):
            return False
            
        self.check_project_specific_setup(worksheet)
        
        print("\n" + "=" * 50)
        print("✅ 모든 진단 완료! Google Sheets API 연결이 정상입니다.")
        print("🚀 main.py를 실행할 준비가 되었습니다.")
        return True

if __name__ == "__main__":
    checker = GoogleAPIChecker()
    success = checker.run_diagnosis()
    
    if not success:
        print("\n❌ 진단 실패. 위의 오류 메시지를 확인하고 문제를 해결하세요.")
        exit(1)
