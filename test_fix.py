#!/usr/bin/env python3
"""
SpreadsheetRow 모델 수정 테스트
"""

from models.spreadsheet_row import SpreadsheetRow

def test_spreadsheet_row_creation():
    """SpreadsheetRow 생성 테스트"""
    print("=== SpreadsheetRow 생성 테스트 ===")
    
    # 기본 생성
    row1 = SpreadsheetRow(
        author_name="이은상",
        onleaf_simple_ratio="1.92%",
        leshine_ratio="4.81%",
        oblible_ratio="93.27%",
        full_message="이름:이은상 온리프 1시간 르샤인 2.5시간 오블리브 48.5시간"
    )
    
    print(f"작성자: {row1.author_name}")
    print(f"금요일 날짜: {row1.friday_date}")
    print(f"온리프/심플 비율: {row1.onleaf_simple_ratio}")
    print(f"르샤인 비율: {row1.leshine_ratio}")
    print(f"오블리브 비율: {row1.oblible_ratio}")
    print(f"전체 메시지:\n{row1.full_message}")
    print()

def test_column_data():
    """열 데이터 반환 테스트"""
    print("=== 열 데이터 반환 테스트 ===")
    
    row = SpreadsheetRow(
        author_name="홍길동",
        onleaf_simple_ratio="10.50%",
        leshine_ratio="20.30%",
        oblible_ratio="69.20%",
        full_message="테스트 메시지입니다"
    )
    
    column_data = row.get_column_data()
    for column, value in column_data.items():
        print(f"{column}열: {value}")
    print()

def test_from_parsed_data():
    """파싱된 데이터로부터 생성 테스트"""
    print("=== 파싱된 데이터로부터 생성 테스트 ===")
    
    parsed_data = {
        'author_name': '김철수',
        'ratios': {
            'onleaf_simple_ratio': '5.25%',
            'leshine_ratio': '15.75%',
            'oblible_ratio': '79.00%'
        },
        'o_column_data': '이름:김철수 온리프 2시간 르샤인 6시간 오블리브 30시간'
    }
    
    row = SpreadsheetRow.from_parsed_data(parsed_data)
    print(f"작성자: {row.author_name}")
    print(f"온리프/심플: {row.onleaf_simple_ratio}")
    print(f"르샤인: {row.leshine_ratio}")
    print(f"오블리브: {row.oblible_ratio}")
    print(f"전체 메시지:\n{row.full_message}")
    print()

def test_dict_compatibility():
    """dict 호환성 테스트"""
    print("=== dict 호환성 테스트 ===")
    
    # dict 형태 데이터
    dict_data = {
        "slack_user_name": "박영희",
        "onleaf_simple_ratio": "3.14%",
        "leshine_ratio": "12.86%", 
        "oblible_ratio": "84.00%",
        "slack_message_content": "이름:박영희 온리프 1.5시간 르샤인 6시간 오블리브 40시간"
    }
    
    print("dict 데이터:")
    for key, value in dict_data.items():
        print(f"  {key}: {value}")
    print()

if __name__ == "__main__":
    test_spreadsheet_row_creation()
    test_column_data()
    test_from_parsed_data()
    test_dict_compatibility()
    print("✅ 모든 테스트 완료")
