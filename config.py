import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """애플리케이션 설정 관리"""
    
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    GOOGLE_SHEETS_CREDENTIALS_PATH = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")
    TARGET_SHEET_NAME = os.getenv("TARGET_SHEET_NAME")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    @classmethod
    def validate(cls):
        """필수 환경변수 검증"""
        required_vars = [
            "SLACK_BOT_TOKEN",
            "GOOGLE_SHEETS_CREDENTIALS_PATH", 
            "GOOGLE_SPREADSHEET_ID",
            "TARGET_SHEET_NAME",
            "GEMINI_API_KEY"
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing)}")
