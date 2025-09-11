from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SpreadsheetRow:
    """스프레드시트 행 데이터 모델"""
    
    # I~O열: 비율 및 메시지 데이터
    onlief_simple_ratio: str = "00.00%"  # I열: 온리프+심플치과 비율
    reserved_j: str = ""                 # J열: 예약
    reserved_k: str = ""                 # K열: 예약
    leshaen_ratio: str = "00.00%"        # L열: 르샤인 비율
    reserved_m: str = ""                 # M열: 예약
    oblive_ratio: str = "00.00%"         # N열: 오블리브 비율
    
    # O열: 전체 메시지 데이터
    full_message: str = ""               # O열: 년도+주차(이름) + 전체 메시지
    
    def to_list(self) -> List[str]:
        """스프레드시트 행으로 변환 (I~O열)"""
        return [
            self.onlief_simple_ratio,
            self.reserved_j,
            self.reserved_k,
            self.leshaen_ratio,
            self.reserved_m,
            self.oblive_ratio,
            self.full_message
        ]
    
    @classmethod
    def from_parsed_data(cls, parsed_data: dict) -> 'SpreadsheetRow':
        """파싱된 데이터로부터 SpreadsheetRow 생성"""
        ratios = parsed_data.get('ratios', {})
        
        return cls(
            onlief_simple_ratio=ratios.get('onlief_simple_ratio', '00.00%'),
            leshaen_ratio=ratios.get('leshaen_ratio', '00.00%'),
            oblive_ratio=ratios.get('oblive_ratio', '00.00%'),
            full_message=parsed_data.get('o_column_data', '')
        )
