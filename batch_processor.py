#!/usr/bin/env python3
"""
새벽 3시 배치 처리 스크립트
"""

import sys
from datetime import datetime
import pytz
from config import Config
from services.batch_queue_service import BatchQueueService
from services.slack_service import SlackService
from services.hybrid_sheets_service import HybridSheetsService
from services.message_parser import WeeklyReportParser
from models.spreadsheet_row import SpreadsheetRow

def process_batch():
    """배치 처리 실행"""
    
    kst = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(kst)
    
    print(f"🌙 배치 처리 시작: {current_time.strftime('%Y-%m-%d %H:%M:%S KST')}")
    
    try:
        Config.validate()
        
        # 서비스 초기화
        queue_service = BatchQueueService()
        slack_service = SlackService(Config.SLACK_BOT_TOKEN)
        excel_service = HybridSheetsService(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
            Config.GOOGLE_SPREADSHEET_ID
        )
        
        # 대기 중인 작업 가져오기
        pending_tasks = queue_service.get_pending_tasks()
        
        if not pending_tasks:
            print("📭 처리할 작업이 없습니다.")
            return True
        
        print(f"📋 처리할 작업: {len(pending_tasks)}개")
        
        processed_count = 0
        failed_count = 0
        
        for task in pending_tasks:
            try:
                print(f"\n🔄 처리 중: {task['id']}")
                
                # 메시지 파싱
                parser = WeeklyReportParser()
                parsed_data = parser.parse_message(task['message_text'])
                
                # 스프레드시트 행 데이터 생성
                row_data = SpreadsheetRow.from_parsed_data(parsed_data, task['author_name'])
                
                # Excel 파일에 데이터 입력 (A, B열 포함)
                row_data_dict = {
                    'A': row_data.author_name,
                    'B': row_data.friday_date,
                    'I': row_data.onleaf_simple_ratio,
                    'L': row_data.leshine_ratio,
                    'N': row_data.oblive_ratio,
                    'O': row_data.memo
                }
                
                row_number = excel_service.update_with_temp_conversion(
                    Config.TARGET_SHEET_NAME,
                    row_data_dict
                )
                
                # 작업 완료 표시
                queue_service.mark_task_completed(task['id'], {
                    'row_number': row_number,
                    'data': row_data_dict
                })
                
                # 완료 알림
                slack_service.send_notification(
                    task['channel_id'],
                    f"✅ 새벽 배치 처리 완료!\n"
                    f"📍 입력 위치: {row_number}행\n"
                    f"👤 작성자: {task['author_name']} (A열)\n"
                    f"📅 금요일 날짜: {row_data.friday_date} (B열)\n"
                    f"📊 비율 데이터: {row_data.onleaf_simple_ratio}(I), {row_data.leshine_ratio}(L), {row_data.oblive_ratio}(N)"
                )
                
                processed_count += 1
                print(f"✅ 완료: {task['id']} → {row_number}행")
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ 실패: {task['id']} - {error_msg}")
                
                # 작업 실패 표시
                queue_service.mark_task_failed(task['id'], error_msg)
                
                # 실패 알림
                try:
                    slack_service.send_notification(
                        task['channel_id'],
                        f"❌ 새벽 배치 처리 실패\n"
                        f"👤 작성자: {task['author_name']}\n"
                        f"🚨 오류: {error_msg}"
                    )
                except:
                    pass
                
                failed_count += 1
        
        # 배치 처리 완료 요약
        print(f"\n🌅 배치 처리 완료:")
        print(f"   ✅ 성공: {processed_count}개")
        print(f"   ❌ 실패: {failed_count}개")
        
        return failed_count == 0
        
    except Exception as e:
        print(f"❌ 배치 처리 시스템 오류: {e}")
        return False

if __name__ == "__main__":
    success = process_batch()
    sys.exit(0 if success else 1)
