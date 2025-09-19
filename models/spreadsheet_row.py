from dataclasses import dataclass
from datetime import datetime, timedelta
import re
from typing import List, Optional

@dataclass
class SpreadsheetRow:
    """스프레드시트 행 데이터 모델"""
    
    # A~B열: 기본 정보
    author_name: str = "홍길동"             # A열: 작성자 이름
    friday_date: str = ""                   # B열: 해당 주 금요일 날짜 (YYYY-MM-DD)
    
    # I, L, N, O열: 비율 및 메시지 데이터  
    onleaf_simple_ratio: str = "00.00%"     # I열: 온리프+심플치과 비율 (오타 수정)
    leshine_ratio: str = "00.00%"           # L열: 르샤인 비율 (오타 수정)
    oblible_ratio: str = "00.00%"           # N열: 오블리브 비율 (오타 수정)
    full_message: str = ""                  # O열: 년도+주차(이름) + 전체 메시지
    
    def __post_init__(self):
        """초기화 후 자동으로 날짜와 메시지 포맷팅"""
        if not self.friday_date:
            self.friday_date = self._get_friday_of_week()
        
        if self.full_message and not self.full_message.startswith('-'):
            # 원본 메시지가 있고 아직 포맷팅되지 않은 경우
            self.full_message = self._format_message_content(self.author_name, self.full_message)
    
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
    
    def get_column_data(self) -> dict:
        """필요한 열의 데이터만 반환"""
        return {
            'A': self.author_name,
            'B': self.friday_date,
            'I': self.onleaf_simple_ratio,
            'L': self.leshine_ratio,
            'N': self.oblible_ratio,
            'O': self.full_message
        }
    
    @classmethod
    def from_parsed_data(cls, parsed_data: dict) -> 'SpreadsheetRow':
        """파싱된 데이터로부터 SpreadsheetRow 생성"""
        ratios = parsed_data.get('ratios', {})
        
        return cls(
            author_name=parsed_data.get('author_name', '홍길동'),
            friday_date=parsed_data.get('friday_date', ''),
            onleaf_simple_ratio=ratios.get('onleaf_simple_ratio', '00.00%'),
            leshine_ratio=ratios.get('leshine_ratio', '00.00%'),
            oblible_ratio=ratios.get('oblible_ratio', '00.00%'),
            full_message=parsed_data.get('o_column_data', '')
        )
