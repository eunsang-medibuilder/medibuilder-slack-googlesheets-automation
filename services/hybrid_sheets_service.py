"""
Excel 파일을 임시로 Google Sheets로 변환하여 작업 후 다시 Excel로 변환
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
import gspread
import time

class HybridSheetsService:
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
    
    def update_with_temp_conversion(self, sheet_name, row_data):
        """임시 변환 방식으로 데이터 업데이트"""
        
        temp_sheets_id = None
        try:
            # 1. Excel을 임시 Google Sheets로 변환
            print("📄 임시 Google Sheets 생성 중...")
            temp_sheets_id = self._create_temp_sheets()
            
            # 2. Google Sheets API로 데이터 수정
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
            updates = []
            for col, value in row_data.items():
                cell = f"{col}{next_row}"
                updates.append({'range': cell, 'values': [[value]]})
            
            # 배치 업데이트
            for update in updates:
                worksheet.update(update['range'], update['values'])
            
            # 3. 다시 Excel로 변환하여 원본 파일 교체
            print("📊 Excel 파일로 변환 중...")
            self._convert_back_to_excel(temp_sheets_id)
            
            print(f"✅ 데이터 입력 완료 (행 {next_row})")
            return next_row
            
        finally:
            # 4. 임시 파일 정리
            if temp_sheets_id:
                self._cleanup_temp_file(temp_sheets_id)
    
    def _create_temp_sheets(self):
        """Excel 파일을 임시 Google Sheets로 변환"""
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
        # Excel 형식으로 내보내기
        request = self.drive_service.files().export_media(
            fileId=sheets_id,
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # 원본 파일 업데이트
        from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
        import io
        
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
    
    def _cleanup_temp_file(self, temp_file_id):
        """임시 파일 삭제"""
        try:
            self.drive_service.files().delete(fileId=temp_file_id).execute()
            print("🗑️ 임시 파일 정리 완료")
        except:
            pass
