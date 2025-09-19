#!/usr/bin/env python3
"""
전체 로직 테스트 스크립트
"""

import json
from datetime import datetime
import pytz
from services.batch_queue_service import BatchQueueService
from services.message_parser import WeeklyReportParser
from models.spreadsheet_row import SpreadsheetRow

def test_full_logic():
    """전체 로직 테스트"""
    
    print("🧪 전체 로직 테스트 시작\n")
    
    # 1. 테스트 메시지
    test_message = """2025년 9월 3주차 주간업무 현황
기간 : 25. 9. 16 ~ 25. 9. 20

금주 완료 작업 소요시간 합계(시간)
온리프 : 1.5
르샤인 : 3.2
오블리브 : 47.3
심플 : 0.5

총합 : 52.5 시간"""
    
    # 2. 메시지 파싱 테스트
    print("1️⃣ 메시지 파싱 테스트...")
    parser = WeeklyReportParser()
    parsed_data = parser.parse_message(test_message)
    
    print(f"   파싱 결과: {json.dumps(parsed_data, ensure_ascii=False, indent=2)}")
    
    # 3. SpreadsheetRow 생성 테스트
    print("\n2️⃣ SpreadsheetRow 생성 테스트...")
    row_data = SpreadsheetRow.from_parsed_data(parsed_data, "테스트사용자")
    
    print(f"   A열 (작성자): {row_data.author_name}")
    print(f"   B열 (금요일): {row_data.friday_date}")
    print(f"   I열 (온리프+심플): {row_data.onleaf_simple_ratio}")
    print(f"   L열 (르샤인): {row_data.leshine_ratio}")
    print(f"   N열 (오블리브): {row_data.oblive_ratio}")
    print(f"   O열 (메모): {row_data.memo[:50]}...")
    
    # 4. 배치 큐 테스트
    print("\n3️⃣ 배치 큐 테스트...")
    queue_service = BatchQueueService("test_queue.json")
    
    success = queue_service.add_to_queue(
        "TEST_CHANNEL",
        "TEST_THREAD",
        "테스트사용자",
        test_message
    )
    
    if success:
        print("   ✅ 큐 등록 성공")
        
        # 큐 상태 확인
        status = queue_service.get_queue_status()
        print(f"   📊 큐 상태: {status}")
        
        # 대기 작업 확인
        pending = queue_service.get_pending_tasks()
        print(f"   📋 대기 작업: {len(pending)}개")
        
    else:
        print("   ❌ 큐 등록 실패")
    
    # 5. 컬럼 데이터 검증
    print("\n4️⃣ 컬럼 데이터 검증...")
    column_data = row_data.get_column_data()
    
    required_columns = ['A', 'B', 'I', 'L', 'N', 'O']
    missing_columns = []
    
    for col in required_columns:
        if col not in column_data or not column_data[col]:
            missing_columns.append(col)
        else:
            print(f"   ✅ {col}열: {column_data[col][:30]}...")
    
    if missing_columns:
        print(f"   ❌ 누락된 열: {missing_columns}")
        return False
    
    print("\n✅ 모든 테스트 통과!")
    return True

if __name__ == "__main__":
    success = test_full_logic()
    if not success:
        exit(1)
