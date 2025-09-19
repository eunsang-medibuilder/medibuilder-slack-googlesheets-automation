#!/usr/bin/env python3
"""
Slack 연결 디버깅 스크립트
"""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import Config

def test_slack_connection():
    """Slack 연결 테스트"""
    try:
        Config.validate()
        client = WebClient(token=Config.SLACK_BOT_TOKEN)
        
        # 봇 정보 확인
        print("🔍 봇 정보 확인 중...")
        auth_response = client.auth_test()
        print(f"✅ 봇 연결 성공: {auth_response['user']}")
        print(f"   팀: {auth_response['team']}")
        print(f"   사용자 ID: {auth_response['user_id']}")
        
        return client
        
    except SlackApiError as e:
        print(f"❌ Slack API 오류: {e.response['error']}")
        return None
    except Exception as e:
        print(f"❌ 일반 오류: {str(e)}")
        return None

def test_channel_access(client, channel_id):
    """채널 접근 테스트"""
    try:
        print(f"\n🔍 채널 접근 테스트: {channel_id}")
        
        # 채널 정보 확인
        channel_info = client.conversations_info(channel=channel_id)
        print(f"✅ 채널 정보: {channel_info['channel']['name']}")
        
        # 최근 메시지 1개 가져오기 테스트
        history = client.conversations_history(channel=channel_id, limit=1)
        print(f"✅ 메시지 조회 성공: {len(history['messages'])}개 메시지")
        
        return True
        
    except SlackApiError as e:
        error_code = e.response.get('error', 'unknown')
        print(f"❌ 채널 접근 실패 ({error_code}): {e.response.get('error', str(e))}")
        
        if error_code == 'channel_not_found':
            print("   → 채널 ID가 올바른지 확인하세요")
        elif error_code == 'not_in_channel':
            print("   → 봇을 채널에 초대하세요")
        elif error_code == 'missing_scope':
            print("   → 봇 권한을 확인하세요 (channels:history, groups:history)")
            
        return False

def test_message_access(client, channel_id, thread_ts):
    """특정 메시지 접근 테스트"""
    try:
        print(f"\n🔍 메시지 접근 테스트: {thread_ts}")
        
        # 단일 메시지 조회
        response = client.conversations_history(
            channel=channel_id,
            latest=thread_ts,
            limit=1,
            inclusive=True
        )
        
        if response['messages']:
            message = response['messages'][0]
            print(f"✅ 메시지 조회 성공")
            print(f"   작성자: {message.get('user', 'unknown')}")
            print(f"   시간: {message.get('ts', 'unknown')}")
            print(f"   내용 길이: {len(message.get('text', ''))}")
            return True
        else:
            print("❌ 메시지를 찾을 수 없습니다")
            return False
            
    except SlackApiError as e:
        error_code = e.response.get('error', 'unknown')
        print(f"❌ 메시지 접근 실패 ({error_code}): {e.response.get('error', str(e))}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("사용법: python debug_slack.py <channel_id> <thread_ts>")
        sys.exit(1)
    
    channel_id = sys.argv[1]
    thread_ts = sys.argv[2]
    
    print("🚀 Slack 연결 디버깅 시작")
    print("=" * 50)
    
    # 1. 봇 연결 테스트
    client = test_slack_connection()
    if not client:
        sys.exit(1)
    
    # 2. 채널 접근 테스트
    if not test_channel_access(client, channel_id):
        sys.exit(1)
    
    # 3. 메시지 접근 테스트
    if not test_message_access(client, channel_id, thread_ts):
        sys.exit(1)
    
    print("\n✅ 모든 테스트 통과!")
