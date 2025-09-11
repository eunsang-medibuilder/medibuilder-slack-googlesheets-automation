import unittest
from services.message_parser import WeeklyReportParser

class TestWeeklyReportParser(unittest.TestCase):
    """주간업무 현황 파서 테스트"""
    
    def setUp(self):
        self.parser = WeeklyReportParser()
        self.sample_message = """2025년 9월 1주차 주간업무 현황
기간 : 25. 9. 1 ~ 25. 9. 5

금주 완료 작업 소요시간 합계(시간)
온리프 : 1
르샤인 : 2.5
오블리브 : 48.5
심플 : 0

총합 : 52 시간

금주 완료 작업 수가 산정(시간 당 24000원)
온리프 :24,000원
르샤인 : 60,000원
오블리브 : 1,164,000원
심플 : 0원

총합 : 1,248,000원

주간 병원별 업무 현황
온리프
신규 작업 : 1건
잔여(진행중) 작업 : 1건
완료 : 1건
홀딩 : 4건

르샤인
신규 작업 : 1건
잔여(진행중) 작업 : 2건
완료 : 3건
홀딩 : 0건

오블리브
신규 작업 : 1건
잔여(진행중) 작업 : 1건
완료 : 2건
홀딩 : 1건

심플치과
신규 작업 : 0건
잔여(진행중) 작업 : 0건
완료 : 0건
홀딩 : 0건"""
    
    def test_parse_message(self):
        """메시지 파싱 테스트"""
        result = self.parser.parse_message(self.sample_message)
        
        # 년도/주차 확인
        self.assertEqual(result['year_week'], '2025 9월 1주차')
        
        # 시간 데이터 확인
        time_data = result['time_data']
        self.assertEqual(time_data['온리프'], 1.0)
        self.assertEqual(time_data['르샤인'], 2.5)
        self.assertEqual(time_data['오블리브'], 48.5)
        self.assertEqual(time_data['심플'], 0.0)
        self.assertEqual(time_data['총합'], 52.0)
        
        # 비율 계산 확인
        ratios = result['ratios']
        self.assertEqual(ratios['onlief_simple_ratio'], '1.92%')  # (1+0)/52*100
        self.assertEqual(ratios['leshaen_ratio'], '4.81%')       # 2.5/52*100
        self.assertEqual(ratios['oblive_ratio'], '93.27%')       # 48.5/52*100
        
        # O열 데이터 확인
        o_data = result['o_column_data']
        self.assertTrue(o_data.startswith('- 2025 9월 1주차(이은상)'))
        self.assertIn(self.sample_message, o_data)
    
    def test_ratio_calculation_with_zero_total(self):
        """총합이 0일 때 비율 계산 테스트"""
        message_with_zero = """2025년 9월 1주차 주간업무 현황
금주 완료 작업 소요시간 합계(시간)
온리프 : 0
르샤인 : 0
오블리브 : 0
심플 : 0

총합 : 0 시간"""
        
        result = self.parser.parse_message(message_with_zero)
        ratios = result['ratios']
        
        self.assertEqual(ratios['onlief_simple_ratio'], '00.00%')
        self.assertEqual(ratios['leshaen_ratio'], '00.00%')
        self.assertEqual(ratios['oblive_ratio'], '00.00%')

if __name__ == '__main__':
    unittest.main()
