import gspread
import re
from datetime import datetime, timedelta
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
    
    def _get_friday_of_week(self) -> str:
        """해당 주의 금요일 날짜를 YYYY-MM-DD 형식으로 반환"""
        today = datetime.now()
        days_until_friday = (4 - today.weekday()) % 7  # 4 = 금요일
        if today.weekday() > 4:  # 토요일(5) 또는 일요일(6)인 경우 다음 주 금요일
            days_until_friday = 7 - today.weekday() + 4
        friday = today + timedelta(days=days_until_friday)
        return friday.strftime("%Y-%m-%d")
    
    def _format_message_content(self, user_name: str, message_content: str) -> str:
        """메시지 내용을 제목과 함께 포맷팅"""
        today = datetime.now()
        year = today.year
        month = today.month
        
        # 해당 월의 첫 번째 날 구하기
        first_day = datetime(year, month, 1)
        # 해당 월 첫 번째 날의 요일 (0=월요일)
        first_weekday = first_day.weekday()
        
        # 현재 날짜가 몇 번째 주인지 계산
        current_day = today.day
        week_number = ((current_day - 1 + first_weekday) // 7) + 1
        
        # 메시지에서 "이름:xxx" 패턴 제거
        cleaned_message = re.sub(r'이름:\S+\s*', '', message_content).strip()
        
        title = f"-{year} {month}월 {week_number}주차({user_name})"
        return f"{title}\n{cleaned_message}"
    
    def append_row(self, data: dict):
        """빈 행에 필요한 열만 데이터 입력 (A, B, I, L, N, O열)"""
        try:
            # 첫 번째 빈 행 찾기
            target_row = self.find_first_empty_row()
            
            # 필요한 열의 데이터만 준비
            column_data = {
                'A': data["slack_user_name"],                    # A열: 사용자명
                'B': self._get_friday_of_week(),                 # B열: 해당 주 금요일
                'I': data["onleaf_simple_ratio"],                # I열: 온리프/심플 비율
                'L': data["leshine_ratio"],                      # L열: 르샤인 비율
                'N': data["oblible_ratio"],                      # N열: 오블리브 비율
                'O': self._format_message_content(               # O열: 제목 + 원본 메시지
                    data["slack_user_name"], 
                    data["slack_message_content"]
                )
            }
            
            # 각 열별로 개별 업데이트
            for column, value in column_data.items():
                if value:  # 값이 있는 경우만 업데이트
                    range_name = f"{column}{target_row}"
                    self.worksheet.update(range_name, [[value]])
            
            print(f"데이터가 {target_row}행에 성공적으로 추가되었습니다.")
            print(f"업데이트된 열: {', '.join(column_data.keys())}")
            
        except Exception as e:
            raise Exception(f"Google Sheets 업데이트 오류: {str(e)}")
    
    def get_last_row_number(self) -> int:
        """마지막 행 번호 반환"""
        return len(self.worksheet.get_all_values())
