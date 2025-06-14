from fastapi import FastAPI, File, UploadFile
import shutil
import os
from utils.spleeter_utils import run_spleeter
from utils.demucs_utils import run_demucs
from utils.rnnoise_utils import run_rnnoise
from utils.silero_utils import run_silero_vad

app = FastAPI()

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/process/{method}")
async def process_audio(method: str, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    output_path = os.path.join(OUTPUT_FOLDER, file.filename)

    if method == "spleeter":
        run_spleeter(file_path, OUTPUT_FOLDER)
    elif method == "demucs":
        run_demucs(file_path)
    elif method == "rnnoise":
        run_rnnoise(file_path, output_path)
    elif method == "silero":
        run_silero_vad(file_path, output_path)
    else:
        return {"error": "Invalid method. Choose spleeter/demucs/rnnoise/silero"}

    return {"status": f"{method} processing complete", "output": output_path}