from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
from utils.spleeter_utils import run_spleeter
from utils.demucs_utils import run_demucs
from utils.rnnoise_utils import run_rnnoise
from utils.silero_utils import run_silero_vad
from uuid import uuid4

app = FastAPI()

# ✅ CORS setup for Vercel frontend
origins = [
    "http://localhost:3000",
    "https://your-frontend.vercel.app",  # replace with your actual frontend domain
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

@app.post("/process/{method}")
async def process_audio(method: str, file: UploadFile = File(...)):
    if not file.filename.endswith(('.wav', '.mp3', '.ogg', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Unique filename to prevent conflicts
    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid4().hex}{extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    output_path = os.path.join(OUTPUT_FOLDER, unique_filename)

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
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

    # ✅ You should ideally serve files using a route
    return {
        "status": "success",
        "processedUrl": f"/download/{unique_filename}"
    }

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)
