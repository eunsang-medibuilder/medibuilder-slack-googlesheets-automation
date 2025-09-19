#!/bin/bash
# 새벽 3시 배치 처리를 위한 cron 설정

PROJECT_DIR="/Users/medibuilder_es.lee/medibuilder-slack-googlesheets-automation"
PYTHON_PATH="/usr/bin/python3"

# cron 작업 추가
echo "⏰ 새벽 3시 배치 처리 cron 설정 중..."

# 기존 cron 백업
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# 새 cron 작업 생성
(crontab -l 2>/dev/null || true; echo "0 3 * * * cd $PROJECT_DIR && $PYTHON_PATH batch_processor.py >> batch_processor.log 2>&1") | crontab -

echo "✅ cron 설정 완료!"
echo "📅 매일 새벽 3시에 배치 처리가 실행됩니다."
echo "📝 로그 파일: $PROJECT_DIR/batch_processor.log"

# 현재 cron 작업 확인
echo ""
echo "📋 현재 cron 작업 목록:"
crontab -l
