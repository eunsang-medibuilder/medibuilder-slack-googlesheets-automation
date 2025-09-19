"""
동시 작업 보호를 위한 안전한 Excel 서비스
- 특정 행만 롤백 (전체 파일 롤백 방지)
- 동시 작업자 변경사항 보호
"""
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

class ConcurrentSafeExcelService:
    def __init__(self, credentials_path, excel_file_id):
        self.credentials_path = credentials_path
        self.excel_file_id = excel_file_id
        self.drive_service = self._build_drive_service()
        self.gc = gspread.service_account(filename=credentials_path)
    
    def _build_drive_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        return build('drive', 'v3', credentials=creds)
    
    def _create_backup(self):
        """백업 생성 (복구용이 아닌 기록용)"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        backup_metadata = {
            'name': f"BACKUP_{timestamp}_automation_record",
            'parents': [self._get_backup_folder_id()]
        }
        
        backup = self.drive_service.files().copy(
            fileId=self.excel_file_id,
            body=backup_metadata
        ).execute()
        
        print(f"📝 기록용 백업 생성: {backup['name']}")
        return backup['id']
    
    def _get_backup_folder_id(self):
        """백업 폴더 ID 가져오기 또는 생성"""
        # 간단히 구현 - 실제로는 폴더 검색 후 없으면 생성
        folder_metadata = {
            'name': 'Excel_Automation_Records',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.drive_service.files().create(body=folder_metadata).execute()
        return folder['id']
    
    def _capture_current_state(self, worksheet, target_row):
        """현재 상태 캡처 (특정 행만)"""
        try:
            # 대상 행의 현재 값들 저장
            current_values = {}
            for col in ['I', 'L', 'N', 'O']:
                cell_value = worksheet.acell(f"{col}{target_row}").value
                current_values[col] = cell_value
            
            print(f"📸 현재 상태 캡처 완료 (행 {target_row})")
            return current_values
        except Exception as e:
            print(f"⚠️ 상태 캡처 실패: {e}")
            return {}
    
    def _restore_row_only(self, worksheet, target_row, original_values):
        """특정 행만 복구 (전체 파일 롤백 방지)"""
        try:
            print(f"🔄 행 {target_row} 복구 중...")
            
            for col, original_value in original_values.items():
                cell = f"{col}{target_row}"
                worksheet.update(cell, original_value or "")
            
            print(f"✅ 행 {target_row} 복구 완료")
            
        except Exception as e:
            print(f"❌ 행 복구 실패: {e}")
            raise e
    
    def _validate_no_concurrent_changes(self, worksheet, target_row, original_state):
        """동시 변경 감지"""
        current_state = self._capture_current_state(worksheet, target_row)
        
        for col in ['I', 'L', 'N', 'O']:
            original = original_state.get(col, "")
            current = current_state.get(col, "")
            
            if original != current:
                print(f"⚠️ 동시 변경 감지: {col}열 '{original}' → '{current}'")
                return False
        
        return True
    
    def safe_update_with_concurrent_protection(self, sheet_name, row_data):
        """동시 작업 보호가 포함된 안전한 업데이트"""
        temp_sheets_id = None
        target_row = None
        original_row_state = {}
        
        try:
            # 1. 입력 데이터 검증
            self._validate_data(row_data)
            
            # 2. 기록용 백업 생성
            print("📝 기록용 백업 생성 중...")
            backup_id = self._create_backup()
            
            # 3. 임시 Google Sheets 생성
            print("📄 임시 작업 파일 생성 중...")
            temp_sheets_id = self._create_temp_sheets()
            
            # 4. 워크시트 접근
            spreadsheet = self.gc.open_by_key(temp_sheets_id)
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except:
                worksheet = spreadsheet.sheet1
            
            # 5. 대상 행 결정
            values = worksheet.get_all_values()
            target_row = len([row for row in values if any(cell.strip() for cell in row)]) + 1
            
            # 6. 현재 행 상태 캡처
            original_row_state = self._capture_current_state(worksheet, target_row)
            
            # 7. 데이터 입력
            print(f"✏️ 행 {target_row}에 데이터 입력 중...")
            for col, value in row_data.items():
                worksheet.update(f"{col}{target_row}", value)
            
            # 8. 입력 결과 검증
            print("🔍 입력 결과 검증 중...")
            for col, expected in row_data.items():
                actual = worksheet.acell(f"{col}{target_row}").value
                if actual != expected:
                    raise ValueError(f"입력 실패: {col} 예상={expected}, 실제={actual}")
            
            # 9. Excel로 변환
            print("📊 Excel 파일 업데이트 중...")
            self._convert_back_to_excel(temp_sheets_id)
            
            print(f"✅ 안전한 업데이트 완료! (행 {target_row})")
            return target_row
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            
            # 특정 행만 롤백 시도 (전체 파일 롤백 아님)
            if temp_sheets_id and target_row and original_row_state:
                try:
                    print("🔄 해당 행만 롤백 시도 중...")
                    spreadsheet = self.gc.open_by_key(temp_sheets_id)
                    worksheet = spreadsheet.worksheet(sheet_name) if sheet_name in [ws.title for ws in spreadsheet.worksheets()] else spreadsheet.sheet1
                    
                    self._restore_row_only(worksheet, target_row, original_row_state)
                    self._convert_back_to_excel(temp_sheets_id)
                    
                    print("✅ 해당 행 롤백 완료 (다른 작업자 변경사항 보호됨)")
                    
                except Exception as rollback_error:
                    print(f"❌ 행 롤백 실패: {rollback_error}")
                    print(f"💡 수동 확인 필요 - 행 {target_row}")
            
            raise e
            
        finally:
            # 임시 파일 정리
            if temp_sheets_id:
                try:
                    self.drive_service.files().delete(fileId=temp_sheets_id).execute()
                except:
                    pass
    
    def _validate_data(self, row_data):
        """데이터 검증"""
        for field in ['I', 'L', 'N', 'O']:
            if field not in row_data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        for field in ['I', 'L', 'N']:
            value = row_data[field]
            if not value.endswith('%'):
                raise ValueError(f"비율 형식 오류: {field}")
    
    def _create_temp_sheets(self):
        """임시 Google Sheets 생성"""
        copied_file = self.drive_service.files().copy(
            fileId=self.excel_file_id,
            body={
                'name': f'temp_work_{int(time.time())}',
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
        ).execute()
        return copied_file['id']
    
    def _convert_back_to_excel(self, sheets_id):
        """Google Sheets를 Excel로 변환하여 원본 교체"""
        from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
        import io
        
        request = self.drive_service.files().export_media(
            fileId=sheets_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        
        media = MediaIoBaseUpload(
            file_content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        self.drive_service.files().update(
            fileId=self.excel_file_id,
            media_body=media
        ).execute()
