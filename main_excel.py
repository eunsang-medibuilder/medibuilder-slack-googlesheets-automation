#!/usr/bin/env python3
"""
Slack 주간업무 현황을 Google Drive Excel 파일에 자동 입력하는 스크립트
"""

import argparse
import sys
from config import Config
from services.slack_service import SlackService
from services.hybrid_sheets_service import HybridSheetsService
from services.message_parser import WeeklyReportParser
from models.spreadsheet_row import SpreadsheetRow

def main():
    """메인 실행 함수"""
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='Slack 주간업무 현황을 Google Drive Excel 파일에 자동 입력')
    parser.add_argument('--channel-id', required=True, help='Slack 채널 ID')
    parser.add_argument('--thread-ts', required=True, help='Slack 스레드 타임스탬프')
    parser.add_argument('--author-name', help='작성자 이름 (지정하지 않으면 Slack에서 자동 추출)')
    
    args = parser.parse_args()
    
    try:
        # 환경변수 검증
        Config.validate()
        
        print("🚀 Slack 메시지 처리 시작...")
        
        # 서비스 초기화
        slack_service = SlackService(Config.SLACK_BOT_TOKEN)
        excel_service = HybridSheetsService(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
            Config.GOOGLE_SPREADSHEET_ID
        )
        
        # Slack 메시지 가져오기
        print(f"📥 Slack 메시지 가져오는 중... (채널: {args.channel_id})")
        message_data = slack_service.get_message(args.channel_id, args.thread_ts)
        
        if not message_data:
            print("❌ 메시지를 찾을 수 없습니다.")
            return False
        
        # 메시지 파싱
        print("🔍 메시지 파싱 중...")
        parser = WeeklyReportParser()
        parsed_data = parser.parse_message(message_data['text'])
        
        # 작성자 정보 처리
        author_name = args.author_name
        if not author_name:
            author_name = slack_service.get_user_name(message_data.get('user', ''))
        
        # 스프레드시트 행 데이터 생성
        row_data = SpreadsheetRow.from_parsed_data(parsed_data, author_name)
        
        print("📊 데이터 입력 중...")
        print(f"   온리프+심플치과: {row_data.onleaf_simple_ratio}")
        print(f"   르샤인: {row_data.leshine_ratio}")
        print(f"   오블리브: {row_data.oblive_ratio}")
        print(f"   메모: {row_data.memo}")
        
        # Excel 파일에 데이터 입력
        row_data_dict = {
            'I': row_data.onleaf_simple_ratio,
            'L': row_data.leshine_ratio,
            'N': row_data.oblive_ratio,
            'O': row_data.memo
        }
        
        row_number = excel_service.update_with_temp_conversion(
            Config.TARGET_SHEET_NAME,
            row_data_dict
        )
        
        print(f"✅ 작업 완료! Excel 파일의 {row_number}행에 데이터가 입력되었습니다.")
        
        # 성공 알림
        slack_service.send_notification(
            args.channel_id,
            f"📊 주간업무 현황이 Excel 파일에 자동 입력되었습니다.\n"
            f"• 행 번호: {row_number}\n"
            f"• 온리프+심플치과: {row_data.onleaf_simple_ratio}\n"
            f"• 르샤인: {row_data.leshine_ratio}\n"
            f"• 오블리브: {row_data.oblive_ratio}"
        )
        
        return True
        
    except Exception as e:
        error_msg = f"❌ 오류 발생: {str(e)}"
        print(error_msg)
        
        # 오류 알림
        try:
            slack_service = SlackService(Config.SLACK_BOT_TOKEN)
            slack_service.send_notification(args.channel_id, error_msg)
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
