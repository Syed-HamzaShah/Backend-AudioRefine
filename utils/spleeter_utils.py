from spleeter.separator import Separator
import os

def run_spleeter(input_path: str, output_dir: str):
    """
    Separates vocals and accompaniment from the input audio using Spleeter (2 stems).
    
    Args:
        input_path (str): Path to the input audio file.
        output_dir (str): Directory where the separated files will be saved.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    os.makedirs(output_dir, exist_ok=True)

    try:
        separator = Separator('spleeter:2stems')
        separator.separate_to_file(audio_descriptor=input_path, destination=output_dir)
        print(f"[Spleeter] Separation complete. Files saved to: {output_dir}")
    except Exception as e:
        raise RuntimeError(f"Spleeter processing failed: {str(e)}")
