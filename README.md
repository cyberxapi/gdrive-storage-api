# Google Drive Storage API

A complete REST API for managing Google Drive files with full CRUD operations (GET, POST, PUT, DELETE). Built with FastAPI and deployable on Render.

## Features

- **List Files**: Get all files or filter by folder
- **Upload Files**: Upload files directly to Google Drive
- **Download Files**: Download files from Google Drive
- **Delete Files**: Remove files from Google Drive
- **Update Metadata**: Rename files and update properties
- **Search**: Search files by name
- **Create Folders**: Create new folders in Google Drive
- **File Information**: Get detailed file metadata
- **API Key Authentication**: Secure access via query parameters
- **CORS Support**: Cross-origin requests enabled
- **Multiple Account Support**: Switch accounts by changing API key

## Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud Project with Drive API enabled
- Service Account JSON credentials from Google Cloud Console

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gdrive-storage-api.git
   cd gdrive-storage-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Add your credentials to .env**
   - `GOOGLE_CREDENTIALS`: Your Google Service Account JSON (as string)
   - `API_KEY`: Your custom API key for authentication

### Running Locally

```bash
python main.py
```

API will be available at `http://localhost:8000`

Access API documentation at `http://localhost:8000/docs`

## API Endpoints

### Health Check
```
GET /health?api_key=YOUR_API_KEY
```

### List Files
```
GET /files?api_key=YOUR_API_KEY&limit=10&folder_id=optional_folder_id
```

### Get File Info
```
GET /files/{file_id}?api_key=YOUR_API_KEY
```

### Upload File
```
POST /upload?api_key=YOUR_API_KEY&folder_id=optional_folder_id
Content-Type: multipart/form-data
Body: file (binary)
```

### Download File
```
GET /download/{file_id}?api_key=YOUR_API_KEY
```

### Delete File
```
DELETE /files/{file_id}?api_key=YOUR_API_KEY
```

### Update File (Rename)
```
PUT /files/{file_id}?api_key=YOUR_API_KEY&name=new_filename
```

### Create Folder
```
POST /folders?api_key=YOUR_API_KEY&folder_name=MyFolder&parent_id=optional_parent_id
```

### Search Files
```
GET /search?api_key=YOUR_API_KEY&q=search_query&limit=10
```

## Usage Examples

### Using cURL

```bash
# List files
curl "https://api.example.com/files?api_key=your-api-key"

# Upload file
curl -X POST -F "file=@document.pdf" "https://api.example.com/upload?api_key=your-api-key"

# Download file
curl -O "https://api.example.com/download/file_id?api_key=your-api-key"

# Delete file
curl -X DELETE "https://api.example.com/files/file_id?api_key=your-api-key"
```

### Using Python

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "https://api.example.com"

# List files
response = requests.get(f"{BASE_URL}/files", params={"api_key": API_KEY})
files = response.json()

# Upload file
with open("file.pdf", "rb") as f:
    files_data = {"file": f}
    response = requests.post(
        f"{BASE_URL}/upload",
        params={"api_key": API_KEY},
        files=files_data
    )
```

## Deployment on Render

### Prerequisites
- GitHub repository with this code
- Render account

### Steps

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name**: gdrive-storage-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Add environment variables:
   - `GOOGLE_CREDENTIALS`: Your Google Service Account JSON
   - `API_KEY`: Your custom API key

7. Deploy!

## Getting Google Drive Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Drive API
4. Create a Service Account
5. Download the JSON key file
6. Convert the JSON to a string and set as `GOOGLE_CREDENTIALS` environment variable

## Response Format

All responses are in JSON format:

```json
{
  "status": "success",
  "message": "Operation completed",
  "data": {}
}
```

Errors:
```json
{
  "detail": "Error message"
}
```

## Security Notes

- Always use HTTPS in production
- Keep your API_KEY secret
- Rotate credentials regularly
- Use environment variables for sensitive data
- Never commit `.env` file to version control

## Troubleshooting

### "Invalid API Key"
- Check that the API key matches the one in your environment variables
- Ensure it's passed as `?api_key=YOUR_KEY` query parameter

### "Google Credentials not found"
- Verify `GOOGLE_CREDENTIALS` is set correctly
- Ensure the JSON is properly formatted as a string

### "Permission denied"
- Check that your Service Account has access to the files
- Verify Google Drive API is enabled in Google Cloud Console

## License

MIT License

## Support

For issues and questions, please create an issue on GitHub.
