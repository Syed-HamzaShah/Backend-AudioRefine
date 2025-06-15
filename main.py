from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import time
from uuid import uuid4

from utils import run_spleeter, run_rnnoise, run_demucs, run_silero_vad

app = FastAPI()

# CORS config for Vercel or localhost
origins = [
    "http://localhost:3000",
    "https://audiorefine.vercel.app",  # 🔁 Replace with actual frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 🧹 Clean up files older than N seconds
def cleanup_old_files(folder: str, age_limit_seconds: int = 3600):
    now = time.time()
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)
            if file_age > age_limit_seconds:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to remove {file_path}: {e}")

@app.post("/process/{method}")
async def process_audio(method: str, request: Request, file: UploadFile = File(...)):
    # 🔍 Validate file extension
    if not file.filename.endswith(('.wav', '.mp3', '.ogg', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 🧼 Clean up old files before processing
    cleanup_old_files(UPLOAD_FOLDER)
    cleanup_old_files(OUTPUT_FOLDER)

    # 📁 Save file with unique name
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    output_path = os.path.join(OUTPUT_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 🧠 Choose processing method
        if method == "spleeter":
            run_spleeter(file_path, OUTPUT_FOLDER)
        elif method == "demucs":
            run_demucs(file_path)
        elif method == "rnnoise":
            run_rnnoise(file_path, output_path)
        elif method == "silero":
            run_silero_vad(file_path, output_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid method")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    # 🌐 Return full download URL
    download_url = f"{request.base_url}download/{unique_filename}"
    return {
        "status": "success",
        "processedUrl": download_url
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # 🎵 Determine proper MIME type
    ext = os.path.splitext(filename)[1].lower()
    media_type = "audio/wav" if ext == ".wav" else "audio/mpeg"

    return FileResponse(file_path, media_type=media_type, filename=filename)
