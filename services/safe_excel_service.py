"""
백업과 검증을 포함한 안전한 Excel 파일 처리 서비스
"""
import time
import hashlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread

class SafeExcelService:
    def __init__(self, credentials_path, excel_file_id):
        self.credentials_path = credentials_path
        self.excel_file_id = excel_file_id
        self.drive_service = self._build_drive_service()
        self.gc = gspread.service_account(filename=credentials_path)
        self.backup_folder_id = None
    
    def _build_drive_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        return build('drive', 'v3', credentials=creds)
    
    def _create_backup_folder(self):
        """백업 폴더 생성 (한 번만)"""
        if self.backup_folder_id:
            return self.backup_folder_id
            
        folder_metadata = {
            'name': 'Excel_Automation_Backups',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = self.drive_service.files().create(body=folder_metadata).execute()
        self.backup_folder_id = folder['id']
        print(f"📁 백업 폴더 생성: {self.backup_folder_id}")
        return self.backup_folder_id
    
    def _create_backup(self):
        """원본 파일 백업"""
        backup_folder_id = self._create_backup_folder()
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # 원본 파일 정보 가져오기
        original_file = self.drive_service.files().get(fileId=self.excel_file_id).execute()
        
        backup_metadata = {
            'name': f"BACKUP_{timestamp}_{original_file['name']}",
            'parents': [backup_folder_id]
        }
        
        backup = self.drive_service.files().copy(
            fileId=self.excel_file_id,
            body=backup_metadata
        ).execute()
        
        print(f"💾 백업 생성: {backup['name']}")
        return backup['id']
    
    def _get_file_checksum(self, file_id):
        """파일 체크섬 계산"""
        try:
            file_metadata = self.drive_service.files().get(
                fileId=file_id, 
                fields='md5Checksum'
            ).execute()
            return file_metadata.get('md5Checksum')
        except:
            return None
    
    def _validate_data_before_write(self, row_data):
        """입력 데이터 검증"""
        required_fields = ['I', 'L', 'N', 'O']
        
        for field in required_fields:
            if field not in row_data:
                raise ValueError(f"필수 필드 누락: {field}")
        
        # 비율 데이터 검증 (I, L, N)
        for field in ['I', 'L', 'N']:
            value = row_data[field]
            if not value.endswith('%'):
                raise ValueError(f"비율 형식 오류: {field} = {value}")
            
            try:
                float_val = float(value.replace('%', ''))
                if float_val < 0 or float_val > 100:
                    raise ValueError(f"비율 범위 오류: {field} = {value}")
            except ValueError:
                raise ValueError(f"비율 숫자 변환 실패: {field} = {value}")
        
        print("✅ 입력 데이터 검증 통과")
    
    def safe_update(self, sheet_name, row_data):
        """안전한 업데이트 (백업 + 검증 + 롤백)"""
        backup_id = None
        temp_sheets_id = None
        original_checksum = None
        
        try:
            # 1. 입력 데이터 검증
            self._validate_data_before_write(row_data)
            
            # 2. 원본 파일 백업
            print("💾 원본 파일 백업 중...")
            backup_id = self._create_backup()
            original_checksum = self._get_file_checksum(self.excel_file_id)
            
            # 3. 임시 Google Sheets 생성
            print("📄 임시 작업 파일 생성 중...")
            temp_sheets_id = self._create_temp_sheets()
            
            # 4. 데이터 입력
            print("✏️ 데이터 입력 중...")
            spreadsheet = self.gc.open_by_key(temp_sheets_id)
            
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except:
                worksheet = spreadsheet.sheet1
            
            # 빈 행 찾기
            values = worksheet.get_all_values()
            next_row = len([row for row in values if any(cell.strip() for cell in row)]) + 1
            
            # 데이터 입력
            for col, value in row_data.items():
                cell = f"{col}{next_row}"
                worksheet.update(cell, value)
            
            # 5. 입력 데이터 검증
            print("🔍 입력 결과 검증 중...")
            for col, expected_value in row_data.items():
                actual_value = worksheet.acell(f"{col}{next_row}").value
                if actual_value != expected_value:
                    raise ValueError(f"데이터 불일치: {col} 예상={expected_value}, 실제={actual_value}")
            
            # 6. Excel로 변환하여 원본 교체
            print("📊 원본 파일 업데이트 중...")
            self._convert_back_to_excel(temp_sheets_id)
            
            # 7. 최종 검증
            new_checksum = self._get_file_checksum(self.excel_file_id)
            if original_checksum and new_checksum == original_checksum:
                raise ValueError("파일이 변경되지 않았습니다 (체크섬 동일)")
            
            print(f"✅ 안전한 업데이트 완료! (행 {next_row})")
            print(f"📋 백업 파일 ID: {backup_id}")
            
            return next_row
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            
            # 롤백 시도
            if backup_id:
                print("🔄 원본 파일 복구 중...")
                try:
                    self._restore_from_backup(backup_id)
                    print("✅ 원본 파일 복구 완료")
                except Exception as restore_error:
                    print(f"❌ 복구 실패: {restore_error}")
                    print(f"💡 수동 복구 필요 - 백업 ID: {backup_id}")
            
            raise e
            
        finally:
            # 임시 파일 정리
            if temp_sheets_id:
                try:
                    self.drive_service.files().delete(fileId=temp_sheets_id).execute()
                except:
                    pass
    
    def _create_temp_sheets(self):
        """임시 Google Sheets 생성"""
        copied_file = self.drive_service.files().copy(
            fileId=self.excel_file_id,
            body={
                'name': f'temp_sheets_{int(time.time())}',
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
    
    def _restore_from_backup(self, backup_id):
        """백업에서 원본 파일 복구"""
        from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
        import io
        
        # 백업 파일 다운로드
        request = self.drive_service.files().get_media(fileId=backup_id)
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_content.seek(0)
        
        # 원본 파일에 백업 내용 복원
        media = MediaIoBaseUpload(
            file_content,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        self.drive_service.files().update(
            fileId=self.excel_file_id,
            media_body=media
        ).execute()
    
    def list_backups(self):
        """백업 파일 목록 조회"""
        if not self.backup_folder_id:
            print("📁 백업 폴더가 없습니다.")
            return []
        
        results = self.drive_service.files().list(
            q=f"parents in '{self.backup_folder_id}'",
            fields="files(id, name, createdTime)"
        ).execute()
        
        backups = results.get('files', [])
        
        print(f"📋 백업 파일 목록 ({len(backups)}개):")
        for backup in backups:
            print(f"   • {backup['name']} (ID: {backup['id']})")
        
        return backups
