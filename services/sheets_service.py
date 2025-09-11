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
    
    def append_row(self, row_data: SpreadsheetRow):
        """새 행 추가 (I~O열에 데이터 입력)"""
        try:
            # I열부터 O열까지 데이터 추가
            values = row_data.to_list()
            
            # 다음 빈 행 찾기
            next_row = len(self.worksheet.get_all_values()) + 1
            
            # I열부터 O열까지 범위 지정 (I=9, O=15)
            range_name = f"I{next_row}:O{next_row}"
            
            self.worksheet.update(range_name, [values])
            
            print(f"데이터가 {next_row}행에 성공적으로 추가되었습니다.")
            
        except Exception as e:
            raise Exception(f"Google Sheets 업데이트 오류: {str(e)}")
    
    def get_last_row_number(self) -> int:
        """마지막 행 번호 반환"""
        return len(self.worksheet.get_all_values())
