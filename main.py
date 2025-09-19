#!/usr/bin/env python3
"""
Slack 주간업무 현황을 Google Sheets에 자동 입력하는 메인 스크립트
"""

import argparse
import sys
from config import Config
from services.slack_service import SlackService
from services.sheets_service import SheetsService
from services.message_parser import WeeklyReportParser
from models.spreadsheet_row import SpreadsheetRow

def main():
    """메인 실행 함수"""
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='Slack 주간업무 현황을 Google Sheets에 자동 입력')
    parser.add_argument('--channel-id', required=True, help='Slack 채널 ID')
    parser.add_argument('--thread-ts', required=True, help='Slack 스레드 타임스탬프')
    parser.add_argument('--author-name', help='작성자 이름 (지정하지 않으면 Slack에서 자동 추출)')
    
    args = parser.parse_args()
    
    try:
        # 환경변수 검증
        Config.validate()
        
        # 서비스 초기화
        slack_service = SlackService(Config.SLACK_BOT_TOKEN)
        sheets_service = SheetsService(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
            Config.GOOGLE_SPREADSHEET_ID,
            Config.TARGET_SHEET_NAME
        )
        parser = WeeklyReportParser()
        
        print("Slack 메시지를 가져오는 중...")
        print(f"채널 ID: {args.channel_id}")
        print(f"스레드 TS: {args.thread_ts}")
        
        # Slack 메시지 가져오기
        message_content = slack_service.get_message_content(
            args.channel_id, 
            args.thread_ts
        )
        
        if not message_content:
            raise Exception("메시지 내용을 가져올 수 없습니다.")
        
        # 작성자 이름 결정 (명령행 인자 > Slack 추출 > 기본값)
        if args.author_name:
            author_name = args.author_name
        else:
            author_name = slack_service.get_message_author(args.channel_id, args.thread_ts)
        
        print(f"작성자: {author_name}")
        print("메시지 파싱 중...")
        
        # 메시지 파싱
        parsed_data = parser.parse_message(message_content, author_name)
        
        # 스프레드시트 행 데이터 생성
        row_data = SpreadsheetRow.from_parsed_data(parsed_data)
        
        print("Google Sheets에 데이터 추가 중...")
        
        # Google Sheets에 데이터 추가
        sheets_service.append_row(row_data)
        
        print("✅ 작업이 성공적으로 완료되었습니다!")
        
        # 파싱된 데이터 출력 (디버깅용)
        print("\n📊 파싱된 데이터:")
        print(f"작성자: {parsed_data['author_name']}")
        print(f"금요일 날짜: {parsed_data['friday_date']}")
        print(f"년도/주차: {parsed_data['year_week']}")
        print(f"비율 - 온리프+심플: {parsed_data['ratios']['onlief_simple_ratio']}")
        print(f"비율 - 르샤인: {parsed_data['ratios']['leshaen_ratio']}")
        print(f"비율 - 오블리브: {parsed_data['ratios']['oblive_ratio']}")
        
    except Exception as e:
        error_msg = f"오류 발생: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Slack에 에러 알림 전송
        try:
            slack_service = SlackService(Config.SLACK_BOT_TOKEN)
            slack_service.send_error_notification(args.channel_id, str(e))
        except Exception as slack_error:
            print(f"Slack 알림 전송 실패: {slack_error}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()
