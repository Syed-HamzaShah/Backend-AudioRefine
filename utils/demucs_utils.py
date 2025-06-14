import subprocess
import os
import shutil
from uuid import uuid4

def run_demucs(input_path: str, output_dir: str = "outputs") -> str:
    """
    Runs Demucs source separation on the given audio file.
    - Saves separated tracks to the `output_dir`.
    - Returns the path to the final merged or selected stem (e.g., vocals).
    - Assumes Demucs is installed and available in the PATH.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Unique output subfolder to avoid overwrite
    session_id = uuid4().hex
    demucs_output = os.path.join("separated", "htdemucs", os.path.splitext(os.path.basename(input_path))[0])
    temp_output_dir = os.path.join(output_dir, session_id)
    os.makedirs(temp_output_dir, exist_ok=True)

    try:
        # Run Demucs command
        result = subprocess.run(
            ["demucs", input_path],
            capture_output=True,
            text=True,
            check=True  # Raises CalledProcessError on failure
        )
        print(f"[Demucs] Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"[Demucs Error] {e.stderr}")
        raise RuntimeError("Demucs processing failed. See logs for details.")

    # Demucs writes to separated/htdemucs/<filename> by default
    if not os.path.exists(demucs_output):
        raise FileNotFoundError("Expected Demucs output directory not found.")

    # Example: Move vocals.wav to our output_dir
    vocals_path = os.path.join(demucs_output, "vocals.wav")
    if not os.path.exists(vocals_path):
        raise FileNotFoundError("Demucs did not produce vocals.wav")

    final_output_path = os.path.join(temp_output_dir, "vocals_demucs.wav")
    shutil.move(vocals_path, final_output_path)

    return final_output_path
