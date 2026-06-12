# VISORA Backend

FastAPI backend for the VISORA security platform.

## Structure

```
backend/
├── app/
│   ├── main.py                          # FastAPI app + CORS + routers
│   ├── core/config.py                   # Settings via pydantic-settings
│   ├── api/routes/
│   │   ├── health.py                    # GET /api/health
│   │   └── cameras.py                   # GET /api/cameras/test-ip-webcam
│   ├── adapters/ip_webcam_adapter.py    # URL builder for IP Webcam Android
│   ├── schemas/camera.py                # Pydantic schemas
│   ├── services/
│   │   ├── camera_connection_service.py # Prepares camera connection data
│   │   └── detection_service.py         # AI detection placeholder
│   ├── infrastructure/storage/
│   │   ├── local_storage.py             # Local storage placeholder
│   │   └── s3_storage_placeholder.py    # AWS S3 placeholder
│   └── models/                          # DB models (future)
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Create virtual environment

```bash
cd backend
python -m venv venv
```

Activate (Windows PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

Activate (Windows CMD):
```cmd
venv\Scripts\activate.bat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create .env file

```bash
copy .env.example .env
```

### 4. Run backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend running at: http://localhost:8000

Interactive docs: http://localhost:8000/api/docs

---

## Test endpoints

### GET /api/health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "VISORA Backend",
  "version": "0.1.0",
  "environment": "local"
}
```

### GET /api/cameras/test-ip-webcam

```bash
curl "http://localhost:8000/api/cameras/test-ip-webcam?host=192.168.18.84&port=8080"
```

Expected response:
```json
{
  "camera_type": "ip_webcam_android",
  "connection_mode": "local_rtsp",
  "input": { "host": "192.168.18.84", "port": 8080 },
  "base_url": "http://192.168.18.84:8080",
  "rtsp_h264_url": "rtsp://192.168.18.84:8080/h264.sdp",
  "snapshot_url": "http://192.168.18.84:8080/shot.jpg",
  "mjpeg_url": "http://192.168.18.84:8080/video",
  "message": "IP Webcam URLs generated successfully. Real stream connection is not enabled yet."
}
```

---

## Notes

### IP Webcam host changes
The camera IP (`192.168.X.X`) changes depending on the network. It is always
passed as a query parameter — never hardcoded. When cameras are registered via
the web interface (future phase), each camera will store its own editable
`host` and `port`.

### Local testing only
Everything runs on `localhost` for now. The frontend (Angular, port 4200) and
this backend (port 8000) communicate locally. No cloud connectivity required.

### AWS is prepared, not implemented
- `STORAGE_PROVIDER=s3` activates `S3StoragePlaceholder` (boto3 not installed yet).
- `CAMERA_CONNECTION_MODE=cloud_ingest` reserved for future AWS Kinesis Video Streams.
- `AWS_REGION` and `AWS_S3_BUCKET` variables exist in `.env.example` but are empty.
- No AWS credentials are stored or required at this stage.

### What is NOT implemented yet
- Real camera stream consumption (no OpenCV)
- Database / ORM
- Authentication
- AI detection models (facial recognition, firearm detection)
- WebSocket events
- AWS S3 upload
- boto3
