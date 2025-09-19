#!/usr/bin/env python3
"""
백업 관리 유틸리티
"""

import argparse
from config import Config
from services.safe_excel_service import SafeExcelService

def main():
    parser = argparse.ArgumentParser(description='백업 관리 도구')
    parser.add_argument('--list', action='store_true', help='백업 목록 조회')
    parser.add_argument('--restore', help='백업 ID로 복구')
    parser.add_argument('--create-backup', action='store_true', help='수동 백업 생성')
    
    args = parser.parse_args()
    
    Config.validate()
    
    service = SafeExcelService(
        Config.GOOGLE_SHEETS_CREDENTIALS_PATH,
        Config.GOOGLE_SPREADSHEET_ID
    )
    
    if args.list:
        service.list_backups()
    elif args.restore:
        print(f"🔄 백업에서 복구 중... (ID: {args.restore})")
        service._restore_from_backup(args.restore)
        print("✅ 복구 완료!")
    elif args.create_backup:
        print("💾 수동 백업 생성 중...")
        backup_id = service._create_backup()
        print(f"✅ 백업 생성 완료: {backup_id}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
