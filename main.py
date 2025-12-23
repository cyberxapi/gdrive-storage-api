from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv
import os
import json
import io
from typing import Optional, List
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="Google Drive Storage API",
    description="Complete REST API for Google Drive file management",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Drive client
def get_drive_service():
    try:
        creds_json = os.getenv("GOOGLE_CREDENTIALS")
        if not creds_json:
            raise ValueError("GOOGLE_CREDENTIALS not found in environment variables")
        
        creds_dict = json.loads(creds_json)
        credentials = Credentials.from_service_account_info(creds_dict)
        service = build('drive', 'v3', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error initializing Drive service: {str(e)}")
        raise

# Authenticate API request
def verify_api_key(api_key: str):
    valid_key = os.getenv("API_KEY")
    if api_key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
async def root():
    return {
        "message": "Google Drive Storage API",
        "version": "1.0.0",
        "endpoints": {
            "list": "/files?api_key=YOUR_API_KEY",
            "upload": "POST /upload?api_key=YOUR_API_KEY",
            "download": "/download/{file_id}?api_key=YOUR_API_KEY",
            "delete": "DELETE /files/{file_id}?api_key=YOUR_API_KEY",
            "info": "/files/{file_id}?api_key=YOUR_API_KEY"
        }
    }

@app.get("/files")
async def list_files(api_key: str = Query(...), folder_id: Optional[str] = None, limit: int = 10):
    """List all files in Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        query = "trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, createdTime, modifiedTime, size, owners, webViewLink)',
            pageSize=limit
        ).execute()
        
        files = results.get('files', [])
        return {
            "status": "success",
            "count": len(files),
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{file_id}")
async def get_file_info(file_id: str, api_key: str = Query(...)):
    """Get file information"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        file_info = service.files().get(
            fileId=file_id,
            fields='id, name, mimeType, createdTime, modifiedTime, size, owners, webViewLink, parents, description'
        ).execute()
        
        return {
            "status": "success",
            "file": file_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), api_key: str = Query(...), folder_id: Optional[str] = None):
    """Upload a file to Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        file_metadata = {'name': file.filename}
        if folder_id:
            file_metadata['parents'] = [folder_id]
        
        content = await file.read()
        file_obj = io.BytesIO(content)
        
        media = MediaFileUpload(
            io.BytesIO(content),
            mimetype=file.content_type,
            resumable=True
        )
        
        file_result = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "file": file_result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_id}")
async def download_file(file_id: str, api_key: str = Query(...)):
    """Download a file from Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        file_info = service.files().get(fileId=file_id, fields='name, mimeType').execute()
        file_name = file_info.get('name')
        
        request = service.files().get_media(fileId=file_id)
        file_obj = io.BytesIO()
        downloader = MediaIoBaseDownload(file_obj, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_obj.seek(0)
        return FileResponse(
            file_obj,
            media_type=file_info.get('mimeType', 'application/octet-stream'),
            filename=file_name
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{file_id}")
async def delete_file(file_id: str, api_key: str = Query(...)):
    """Delete a file from Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        service.files().delete(fileId=file_id).execute()
        
        return {
            "status": "success",
            "message": f"File {file_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/files/{file_id}")
async def update_file(file_id: str, name: Optional[str] = None, api_key: str = Query(...)):
    """Update file metadata (like rename)"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        file_metadata = {}
        if name:
            file_metadata['name'] = name
        
        updated_file = service.files().update(
            fileId=file_id,
            body=file_metadata,
            fields='id, name, modifiedTime'
        ).execute()
        
        return {
            "status": "success",
            "message": "File updated successfully",
            "file": updated_file
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/folders")
async def create_folder(folder_name: str = Query(...), api_key: str = Query(...), parent_id: Optional[str] = None):
    """Create a folder in Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id, name'
        ).execute()
        
        return {
            "status": "success",
            "message": "Folder created successfully",
            "folder": folder
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
async def search_files(q: str = Query(...), api_key: str = Query(...), limit: int = 10):
    """Search for files in Google Drive"""
    try:
        verify_api_key(api_key)
        service = get_drive_service()
        
        results = service.files().list(
            q=f"name contains '{q}' and trashed=false",
            spaces='drive',
            fields='files(id, name, mimeType, createdTime)',
            pageSize=limit
        ).execute()
        
        files = results.get('files', [])
        return {
            "status": "success",
            "query": q,
            "count": len(files),
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
