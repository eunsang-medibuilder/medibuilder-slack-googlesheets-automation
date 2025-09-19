#!/usr/bin/env python3
"""
배치 시스템 관리 도구
"""

import argparse
import json
from services.batch_queue_service import BatchQueueService

def main():
    parser = argparse.ArgumentParser(description='배치 시스템 관리')
    parser.add_argument('--status', action='store_true', help='큐 상태 조회')
    parser.add_argument('--list', action='store_true', help='대기 중인 작업 목록')
    parser.add_argument('--clear-completed', action='store_true', help='완료된 작업 정리')
    parser.add_argument('--test-run', action='store_true', help='배치 처리 테스트 실행')
    
    args = parser.parse_args()
    
    queue_service = BatchQueueService()
    
    if args.status:
        status = queue_service.get_queue_status()
        print("📊 배치 큐 상태:")
        print(f"   전체: {status['total']}개")
        print(f"   대기 중: {status['pending']}개")
        print(f"   완료: {status['completed']}개")
        print(f"   실패: {status['failed']}개")
    
    elif args.list:
        tasks = queue_service.get_pending_tasks()
        print(f"📋 대기 중인 작업 ({len(tasks)}개):")
        for task in tasks:
            print(f"   • {task['id']} - {task['author_name']} ({task['created_at']})")
    
    elif args.clear_completed:
        queue = queue_service._load_queue()
        before_count = len(queue)
        
        # 완료된 작업만 제거
        queue = [task for task in queue if task['status'] != 'completed']
        queue_service._save_queue(queue)
        
        after_count = len(queue)
        removed_count = before_count - after_count
        
        print(f"🗑️ 완료된 작업 {removed_count}개 정리 완료")
    
    elif args.test_run:
        print("🧪 배치 처리 테스트 실행...")
        from batch_processor import process_batch
        success = process_batch()
        print(f"테스트 결과: {'성공' if success else '실패'}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
