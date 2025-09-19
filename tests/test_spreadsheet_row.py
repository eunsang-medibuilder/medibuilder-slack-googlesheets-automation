import unittest
from models.spreadsheet_row import SpreadsheetRow

class TestSpreadsheetRow(unittest.TestCase):
    """SpreadsheetRow 모델 테스트"""
    
    def test_get_column_data(self):
        """열 데이터 반환 테스트"""
        row = SpreadsheetRow(
            author_name="테스트사용자",
            friday_date="2025-09-05",
            onleaf_simple_ratio="1.92%",
            leshine_ratio="4.81%",
            oblible_ratio="93.27%",
            full_message="- 2025 9월 1주차(테스트사용자)\n테스트 메시지"
        )
        
        column_data = row.get_column_data()
        
        self.assertEqual(column_data['A'], "테스트사용자")
        self.assertEqual(column_data['B'], "2025-09-05")
        self.assertEqual(column_data['I'], "1.92%")
        self.assertEqual(column_data['L'], "4.81%")
        self.assertEqual(column_data['N'], "93.27%")
        self.assertEqual(column_data['O'], "- 2025 9월 1주차(테스트사용자)\n테스트 메시지")
    
    def test_from_parsed_data(self):
        """파싱된 데이터로부터 생성 테스트"""
        parsed_data = {
            'author_name': '홍길동',
            'friday_date': '2025-09-12',
            'ratios': {
                'onleaf_simple_ratio': '10.00%',
                'leshine_ratio': '20.00%',
                'oblible_ratio': '70.00%'
            },
            'o_column_data': '- 2025 9월 2주차(홍길동)\n테스트'
        }
        
        row = SpreadsheetRow.from_parsed_data(parsed_data)
        
        self.assertEqual(row.author_name, '홍길동')
        self.assertEqual(row.friday_date, '2025-09-12')
        self.assertEqual(row.onleaf_simple_ratio, '10.00%')
        self.assertEqual(row.leshine_ratio, '20.00%')
        self.assertEqual(row.oblible_ratio, '70.00%')
        self.assertEqual(row.full_message, '- 2025 9월 2주차(홍길동)\n테스트')
    
    def test_default_values(self):
        """기본값 테스트 (자동 날짜 설정 고려)"""
        row = SpreadsheetRow()
        
        self.assertEqual(row.author_name, "홍길동")
        # friday_date는 자동으로 설정되므로 빈 문자열이 아님
        self.assertNotEqual(row.friday_date, "")
        self.assertTrue(row.friday_date.startswith("2025-"))
        self.assertEqual(row.onleaf_simple_ratio, "00.00%")
        self.assertEqual(row.leshine_ratio, "00.00%")
        self.assertEqual(row.oblible_ratio, "00.00%")
        self.assertEqual(row.full_message, "")
    
    def test_auto_formatting(self):
        """자동 포맷팅 테스트"""
        row = SpreadsheetRow(
            author_name="김철수",
            full_message="이름:김철수 온리프 2시간 르샤인 5시간"
        )
        
        # 자동으로 날짜가 설정되어야 함
        self.assertNotEqual(row.friday_date, "")
        
        # 메시지가 자동으로 포맷팅되어야 함
        self.assertTrue(row.full_message.startswith("-2025"))
        self.assertIn("김철수", row.full_message)
        self.assertNotIn("이름:김철수", row.full_message)  # 이름 패턴 제거 확인

if __name__ == '__main__':
    unittest.main()
