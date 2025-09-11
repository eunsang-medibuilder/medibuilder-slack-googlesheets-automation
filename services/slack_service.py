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
            response = self.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            return response['messages']
        except SlackApiError as e:
            raise Exception(f"Slack API 오류: {e.response['error']}")
    
    def get_message_content(self, channel_id: str, thread_ts: str) -> str:
        """스레드의 첫 번째 메시지 내용 가져오기"""
        messages = self.get_thread_messages(channel_id, thread_ts)
        if messages:
            return messages[0].get('text', '')
        return ""
    
    def send_error_notification(self, channel_id: str, error_message: str):
        """에러 알림 전송"""
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                text=f"⚠️ 오류 발생: {error_message}"
            )
        except SlackApiError as e:
            print(f"Slack 알림 전송 실패: {e.response['error']}")
