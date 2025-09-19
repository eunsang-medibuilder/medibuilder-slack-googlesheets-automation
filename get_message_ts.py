#!/usr/bin/env python3
import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

def get_recent_messages(channel_id, limit=10):
    """최근 메시지들의 ts 값을 조회"""
    try:
        response = client.conversations_history(
            channel=channel_id,
            limit=limit
        )
        
        for message in response['messages']:
            text = message.get('text', '')[:50]  # 첫 50자만 표시
            ts = message.get('ts')
            user = message.get('user', 'Unknown')
            
            print(f"TS: {ts}")
            print(f"User: {user}")
            print(f"Text: {text}...")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    channel_id = input("Channel ID를 입력하세요: ")
    get_recent_messages(channel_id)
