import re
from typing import Dict, Optional
from datetime import datetime, timedelta

class WeeklyReportParser:
    """주간업무 현황 메시지 파싱 클래스"""
    
    def parse_message(self, message: str, author_name: str = "홍길동") -> Dict:
        """Slack 메시지를 파싱하여 필요한 데이터 추출"""
        
        # 년도와 주차 추출
        year_week = self._extract_year_week(message)
        
        # 해당 주 금요일 날짜 계산
        friday_date = self._calculate_friday_date(message)
        
        # 완료 작업 소요시간 추출
        time_data = self._extract_completion_times(message)
        
        # 비율 계산 (I~N열)
        ratios = self._calculate_ratios(time_data)
        
        # O열 데이터 생성
        o_column_data = self._generate_o_column_data(year_week, author_name, message)
        
        return {
            'author_name': author_name,
            'friday_date': friday_date,
            'year_week': year_week,
            'time_data': time_data,
            'ratios': ratios,
            'o_column_data': o_column_data
        }
    
    def _extract_year_week(self, message: str) -> str:
        """년도와 주차 추출"""
        pattern = r'(\d{4})년\s*(\d+)월\s*(\d+)주차'
        match = re.search(pattern, message)
        if match:
            year, month, week = match.groups()
            return f"{year} {month}월 {week}주차"
        return "2025 9월 1주차"  # 기본값
    
    def _calculate_friday_date(self, message: str) -> str:
        """해당 주의 금요일 날짜 계산"""
        # 기간 정보에서 날짜 추출
        period_pattern = r'기간\s*:\s*(\d{2})\.\s*(\d{1,2})\.\s*(\d{1,2})\s*~\s*(\d{2})\.\s*(\d{1,2})\.\s*(\d{1,2})'
        match = re.search(period_pattern, message)
        
        if match:
            start_year, start_month, start_day, end_year, end_month, end_day = match.groups()
            
            # 20XX 형태로 년도 변환
            start_year = f"20{start_year}"
            end_year = f"20{end_year}"
            
            try:
                # 시작일로부터 해당 주의 금요일 찾기
                start_date = datetime(int(start_year), int(start_month), int(start_day))
                
                # 시작일의 요일 확인 (0=월요일, 6=일요일)
                weekday = start_date.weekday()
                
                # 해당 주의 금요일 계산 (4=금요일)
                days_to_friday = 4 - weekday
                friday_date = start_date + timedelta(days=days_to_friday)
                
                return friday_date.strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        # 기본값: 현재 날짜 기준 이번 주 금요일
        today = datetime.now()
        days_to_friday = 4 - today.weekday()
        if days_to_friday < 0:  # 이미 금요일이 지났으면 다음 주 금요일
            days_to_friday += 7
        friday = today + timedelta(days=days_to_friday)
        return friday.strftime('%Y-%m-%d')
    
    def _extract_completion_times(self, message: str) -> Dict[str, float]:
        """완료 작업 소요시간 추출"""
        time_data = {}
        
        # "금주 완료 작업 소요시간 합계(시간)" 섹션 찾기
        lines = message.split('\n')
        in_time_section = False
        
        for line in lines:
            if '금주 완료 작업 소요시간 합계' in line:
                in_time_section = True
                continue
            
            if in_time_section:
                if '총합' in line:
                    # 총합 추출
                    total_match = re.search(r'총합\s*:\s*([\d.]+)', line)
                    if total_match:
                        time_data['총합'] = float(total_match.group(1))
                    break
                
                # 각 병원별 시간 추출
                for hospital in ['온리프', '르샤인', '오블리브', '심플']:
                    if hospital in line:
                        time_match = re.search(rf'{hospital}\s*:\s*([\d.]+)', line)
                        if time_match:
                            time_data[hospital] = float(time_match.group(1))
        
        return time_data
    
    def _calculate_ratios(self, time_data: Dict[str, float]) -> Dict[str, str]:
        """비율 계산 (온리프+심플치과 합쳐서 계산)"""
        ratios = {}
        
        try:
            total = time_data.get('총합', 0)
            if total == 0:
                return {
                    'onlief_simple_ratio': '00.00%',
                    'leshaen_ratio': '00.00%', 
                    'oblive_ratio': '00.00%'
                }
            
            # 온리프 + 심플치과 합계
            onlief_time = time_data.get('온리프', 0)
            simple_time = time_data.get('심플', 0)
            onlief_simple_total = onlief_time + simple_time
            
            leshaen_time = time_data.get('르샤인', 0)
            oblive_time = time_data.get('오블리브', 0)
            
            # 비율 계산
            ratios['onlief_simple_ratio'] = f"{(onlief_simple_total / total * 100):.2f}%"
            ratios['leshaen_ratio'] = f"{(leshaen_time / total * 100):.2f}%"
            ratios['oblive_ratio'] = f"{(oblive_time / total * 100):.2f}%"
            
        except (ValueError, ZeroDivisionError):
            ratios = {
                'onlief_simple_ratio': '00.00%',
                'leshaen_ratio': '00.00%',
                'oblive_ratio': '00.00%'
            }
        
        return ratios
    
    def _generate_o_column_data(self, year_week: str, author_name: str, message: str) -> str:
        """O열 데이터 생성"""
        header = f"- {year_week}({author_name})"
        return f"{header}\n{message}"
