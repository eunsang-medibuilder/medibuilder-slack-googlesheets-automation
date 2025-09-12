import unittest
from models.spreadsheet_row import SpreadsheetRow

class TestSpreadsheetRow(unittest.TestCase):
    """SpreadsheetRow 모델 테스트"""
    
    def test_get_column_data(self):
        """열 데이터 반환 테스트"""
        row = SpreadsheetRow(
            author_name="테스트사용자",
            friday_date="2025-09-05",
            onlief_simple_ratio="1.92%",
            leshaen_ratio="4.81%",
            oblive_ratio="93.27%",
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
                'onlief_simple_ratio': '10.00%',
                'leshaen_ratio': '20.00%',
                'oblive_ratio': '70.00%'
            },
            'o_column_data': '- 2025 9월 2주차(홍길동)\n테스트'
        }
        
        row = SpreadsheetRow.from_parsed_data(parsed_data)
        
        self.assertEqual(row.author_name, '홍길동')
        self.assertEqual(row.friday_date, '2025-09-12')
        self.assertEqual(row.onlief_simple_ratio, '10.00%')
        self.assertEqual(row.leshaen_ratio, '20.00%')
        self.assertEqual(row.oblive_ratio, '70.00%')
        self.assertEqual(row.full_message, '- 2025 9월 2주차(홍길동)\n테스트')
    
    def test_default_values(self):
        """기본값 테스트"""
        row = SpreadsheetRow()
        
        self.assertEqual(row.author_name, "홍길동")
        self.assertEqual(row.friday_date, "")
        self.assertEqual(row.onlief_simple_ratio, "00.00%")
        self.assertEqual(row.leshaen_ratio, "00.00%")
        self.assertEqual(row.oblive_ratio, "00.00%")
        self.assertEqual(row.full_message, "")

if __name__ == '__main__':
    unittest.main()
