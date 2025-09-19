#!/usr/bin/env python3
"""
안전한 Excel 파일 자동화 스크립트 (백업 + 검증 + 롤백)
"""

import argparse
import sys
from config import Config
from services.slack_service import SlackService
from services.safe_excel_service import SafeExcelService
from services.message_parser import WeeklyReportParser
from models.spreadsheet_row import SpreadsheetRow

def main():
    """안전한 메인 실행 함수"""
    
    parser = argparse.ArgumentParser(description='안전한 Excel 파일 자동화')
    parser.add_argument('--channel-id', required=True, help='Slack 채널 ID')
    parser.add_argument('--thread-ts', required=True, help='Slack 스레드 타임스탬프')
    parser.add_argument('--author-name', help='작성자 이름')
    parser.add_argument('--dry-run', action='store_true', help='실제 파일 수정 없이 테스트만')
    
    args = parser.parse_args()
    
    try:
        Config.validate()
        
        print("🛡️ 안전한 Excel 자동화 시작...")
        
        # 서비스 초기화
        slack_service = SlackService(Config.SLACK_BOT_TOKEN)
        safe_excel_service = SafeExcelService(
            Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
            Config.GOOGLE_SPREADSHEET_ID
        )
        
        # Slack 메시지 가져오기
        print(f"📥 Slack 메시지 가져오는 중...")
        message_data = slack_service.get_message(args.channel_id, args.thread_ts)
        
        if not message_data:
            raise ValueError("메시지를 찾을 수 없습니다.")
        
        # 메시지 파싱
        print("🔍 메시지 파싱 중...")
        parser = WeeklyReportParser()
        parsed_data = parser.parse_message(message_data['text'])
        
        # 작성자 정보 처리
        author_name = args.author_name or slack_service.get_user_name(message_data.get('user', ''))
        
        # 스프레드시트 행 데이터 생성
        row_data = SpreadsheetRow.from_parsed_data(parsed_data, author_name)
        
        # 입력할 데이터 미리보기
        print("\n📊 입력 예정 데이터:")
        print(f"   I열 (온리프+심플): {row_data.onleaf_simple_ratio}")
        print(f"   L열 (르샤인): {row_data.leshine_ratio}")
        print(f"   N열 (오블리브): {row_data.oblive_ratio}")
        print(f"   O열 (메모): {row_data.memo}")
        
        row_data_dict = {
            'I': row_data.onleaf_simple_ratio,
            'L': row_data.leshine_ratio,
            'N': row_data.oblive_ratio,
            'O': row_data.memo
        }
        
        if args.dry_run:
            print("\n🧪 DRY-RUN 모드: 실제 파일 수정 없음")
            print("✅ 데이터 검증 완료 - 실제 실행 시 정상 작동할 것으로 예상됩니다.")
            return True
        
        # 사용자 확인
        print(f"\n⚠️ 중요한 파일을 수정합니다!")
        print(f"📄 파일 ID: {Config.GOOGLE_SPREADSHEET_ID}")
        print(f"📋 시트명: {Config.TARGET_SHEET_NAME}")
        
        confirm = input("계속하시겠습니까? (y/N): ").lower().strip()
        if confirm != 'y':
            print("❌ 사용자가 취소했습니다.")
            return False
        
        # 안전한 업데이트 실행
        print("\n🛡️ 안전한 업데이트 시작...")
        row_number = safe_excel_service.safe_update(
            Config.TARGET_SHEET_NAME,
            row_data_dict
        )
        
        print(f"\n✅ 작업 완료!")
        print(f"📍 입력 위치: {row_number}행")
        print(f"💾 백업 폴더에서 복구 가능")
        
        # 성공 알림
        slack_service.send_notification(
            args.channel_id,
            f"🛡️ 안전한 Excel 자동화 완료!\n"
            f"• 입력 행: {row_number}\n"
            f"• 백업 생성됨\n"
            f"• 온리프+심플: {row_data.onleaf_simple_ratio}\n"
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
            slack_service.send_notification(
                args.channel_id, 
                f"🚨 Excel 자동화 실패!\n{error_msg}\n💾 백업에서 복구 가능"
            )
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
