from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import List, Dict, Optional

class SlackService:
    """Slack API 처리 서비스"""
    
    def __init__(self, token: str):
        self.client = WebClient(token=token)
    
    def get_thread_messages(self, channel_id: str, thread_ts: str) -> List[Dict]:
        """스레드의 모든 메시지 가져오기"""
        try:
            # 먼저 단일 메시지 조회 시도
            try:
                response = self.client.conversations_history(
                    channel=channel_id,
                    latest=thread_ts,
                    limit=1,
                    inclusive=True
                )
                if response['messages']:
                    return response['messages']
            except SlackApiError:
                pass
            
            # 스레드 메시지 조회 시도
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            return response['messages']
        except SlackApiError as e:
            error_code = e.response.get('error', 'unknown')
            if error_code == 'thread_not_found':
                raise Exception(f"스레드를 찾을 수 없습니다. thread_ts가 올바른지 확인하세요: {thread_ts}")
            elif error_code == 'channel_not_found':
                raise Exception(f"채널을 찾을 수 없습니다. channel_id가 올바른지 확인하세요: {channel_id}")
            elif error_code == 'not_in_channel':
                raise Exception(f"봇이 채널에 참여하지 않았습니다. 채널에 봇을 초대하세요: {channel_id}")
            else:
                raise Exception(f"Slack API 오류 ({error_code}): {e.response.get('error', str(e))}")
    
    def get_message_content(self, channel_id: str, thread_ts: str) -> str:
        """스레드의 첫 번째 메시지 내용 가져오기"""
        messages = self.get_thread_messages(channel_id, thread_ts)
        if messages:
            return messages[0].get('text', '')
        return ""
    
    def get_message_author(self, channel_id: str, thread_ts: str) -> str:
        """메시지 작성자 이름 가져오기"""
        try:
            messages = self.get_thread_messages(channel_id, thread_ts)
            if messages:
                user_id = messages[0].get('user')
                if user_id:
                    user_info = self.client.users_info(user=user_id)
                    return user_info['user'].get('real_name', '홍길동')
            return '홍길동'
        except SlackApiError:
            return '홍길동'
    
    def send_error_notification(self, channel_id: str, error_message: str):
        """에러 알림 전송"""
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"⚠️ 오류 발생: {error_message}"
            )
        except SlackApiError as e:
            print(f"Slack 알림 전송 실패: {e.response['error']}")
