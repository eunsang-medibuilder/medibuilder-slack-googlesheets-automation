#!/usr/bin/env python3
"""
Slack 메시지를 배치 큐에 등록 (즉시 실행)
"""

import argparse
import sys
from config import Config
from services.slack_service import SlackService
from services.batch_queue_service import BatchQueueService

def main():
    """메시지를 배치 큐에 등록"""
    
    parser = argparse.ArgumentParser(description='Slack 메시지를 새벽 배치 처리 큐에 등록')
    parser.add_argument('--channel-id', required=True, help='Slack 채널 ID')
    parser.add_argument('--thread-ts', required=True, help='Slack 스레드 타임스탬프')
    parser.add_argument('--author-name', help='작성자 이름')
    
    args = parser.parse_args()
    
    try:
        Config.validate()
        
        print("📥 Slack 메시지 가져오는 중...")
        
        # Slack 서비스 초기화
        slack_service = SlackService(Config.SLACK_BOT_TOKEN)
        
        # 메시지 가져오기
        message_data = slack_service.get_message(args.channel_id, args.thread_ts)
        
        if not message_data:
            raise ValueError("메시지를 찾을 수 없습니다.")
        
        # 작성자 정보 처리
        author_name = args.author_name
        if not author_name:
            author_name = slack_service.get_user_name(message_data.get('user', ''))
        
        # 배치 큐에 추가
        queue_service = BatchQueueService()
        success = queue_service.add_to_queue(
            args.channel_id,
            args.thread_ts,
            author_name,
            message_data['text']
        )
        
        if success:
            # 큐 상태 조회
            status = queue_service.get_queue_status()
            
            print(f"\n📊 현재 큐 상태:")
            print(f"   대기 중: {status['pending']}개")
            print(f"   완료: {status['completed']}개")
            print(f"   실패: {status['failed']}개")
            
            # Slack 알림
            slack_service.send_notification(
                args.channel_id,
                f"⏰ 주간업무 현황이 배치 큐에 등록되었습니다.\n"
                f"📅 처리 예정: 다음 새벽 3시 (KST)\n"
                f"👤 작성자: {author_name}\n"
                f"📊 대기 중인 작업: {status['pending']}개\n"
                f"📋 입력 예정 열: A(이름), B(날짜), I, L, N, O"
            )
            
            return True
        else:
            return False
        
    except Exception as e:
        error_msg = f"❌ 큐 등록 실패: {str(e)}"
        print(error_msg)
        
        try:
            slack_service = SlackService(Config.SLACK_BOT_TOKEN)
            slack_service.send_notification(args.channel_id, error_msg)
        except:
            pass
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
