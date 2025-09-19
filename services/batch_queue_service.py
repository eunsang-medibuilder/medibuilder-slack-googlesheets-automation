"""
새벽 배치 처리를 위한 작업 큐 시스템
"""
import json
import os
from datetime import datetime
import pytz

class BatchQueueService:
    def __init__(self, queue_file_path="batch_queue.json"):
        self.queue_file_path = queue_file_path
        self.kst = pytz.timezone('Asia/Seoul')
    
    def add_to_queue(self, channel_id, thread_ts, author_name, message_text):
        """작업을 큐에 추가"""
        
        # 기존 큐 로드
        queue = self._load_queue()
        
        # 새 작업 추가
        task = {
            'id': f"{channel_id}_{thread_ts}",
            'channel_id': channel_id,
            'thread_ts': thread_ts,
            'author_name': author_name,
            'message_text': message_text,
            'created_at': datetime.now(self.kst).isoformat(),
            'status': 'pending'
        }
        
        # 중복 체크
        existing_ids = [t['id'] for t in queue]
        if task['id'] in existing_ids:
            print(f"⚠️ 이미 큐에 있는 작업: {task['id']}")
            return False
        
        queue.append(task)
        self._save_queue(queue)
        
        print(f"✅ 배치 큐에 추가됨: {task['id']}")
        print(f"📅 처리 예정: 다음 새벽 3시 (KST)")
        
        return True
    
    def get_pending_tasks(self):
        """대기 중인 작업 목록 반환"""
        queue = self._load_queue()
        return [task for task in queue if task['status'] == 'pending']
    
    def mark_task_completed(self, task_id, result=None):
        """작업 완료 표시"""
        queue = self._load_queue()
        
        for task in queue:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now(self.kst).isoformat()
                if result:
                    task['result'] = result
                break
        
        self._save_queue(queue)
    
    def mark_task_failed(self, task_id, error_msg):
        """작업 실패 표시"""
        queue = self._load_queue()
        
        for task in queue:
            if task['id'] == task_id:
                task['status'] = 'failed'
                task['failed_at'] = datetime.now(self.kst).isoformat()
                task['error'] = error_msg
                break
        
        self._save_queue(queue)
    
    def _load_queue(self):
        """큐 파일 로드"""
        if not os.path.exists(self.queue_file_path):
            return []
        
        try:
            with open(self.queue_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _save_queue(self, queue):
        """큐 파일 저장"""
        with open(self.queue_file_path, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
    
    def get_queue_status(self):
        """큐 상태 조회"""
        queue = self._load_queue()
        
        status_count = {}
        for task in queue:
            status = task['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            'total': len(queue),
            'pending': status_count.get('pending', 0),
            'completed': status_count.get('completed', 0),
            'failed': status_count.get('failed', 0)
        }
