import gspread
from google.oauth2.service_account import Credentials
from typing import List
from models.spreadsheet_row import SpreadsheetRow

class SheetsService:
    """Google Sheets API 처리 서비스"""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str, sheet_name: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self._setup_client()
    
    def _setup_client(self):
        """Google Sheets 클라이언트 설정"""
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(
            self.credentials_path, 
            scopes=scope
        )
        
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
        self.worksheet = self.spreadsheet.worksheet(self.sheet_name)
    
    def find_first_empty_row(self) -> int:
        """첫 번째 빈 행 찾기"""
        all_values = self.worksheet.get_all_values()
        
        for i, row in enumerate(all_values, 1):
            # A열이 비어있으면 빈 행으로 판단
            if not row or not row[0].strip():
                return i
        
        # 모든 행이 차있으면 다음 행 반환
        return len(all_values) + 1
    
    def append_row(self, row_data: SpreadsheetRow):
        """빈 행에 데이터 추가 (A, B, I~O열)"""
        try:
            # 첫 번째 빈 행 찾기
            target_row = self.find_first_empty_row()
            
            # A~O열 전체 데이터 준비
            values = row_data.to_list()
            
            # A열부터 O열까지 범위 지정 (A=1, O=15)
            range_name = f"A{target_row}:O{target_row}"
            
            self.worksheet.update(range_name, [values])
            
            print(f"데이터가 {target_row}행에 성공적으로 추가되었습니다.")
            
        except Exception as e:
            raise Exception(f"Google Sheets 업데이트 오류: {str(e)}")
    
    def get_last_row_number(self) -> int:
        """마지막 행 번호 반환"""
        return len(self.worksheet.get_all_values())
