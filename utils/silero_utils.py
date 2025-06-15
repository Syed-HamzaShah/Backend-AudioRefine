import torchaudio
import torch
import numpy as np
import soundfile as sf
from silero_vad import get_speech_timestamps, read_audio, save_audio
import os

def run_silero_vad(input_path: str, output_path: str):
    """
    Applies Silero Voice Activity Detection (VAD) to an input audio file.
    Removes non-speech regions and writes the cleaned audio to output_path.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Where to save the VAD-filtered audio.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    sampling_rate = 16000

    # Read and resample the audio
    wav = read_audio(input_path, sampling_rate=sampling_rate)

    # Get timestamps where speech is detected
    speech_timestamps = get_speech_timestamps(wav, sampling_rate=sampling_rate)

    if not speech_timestamps:
        raise ValueError("No speech detected in the audio.")

    # Concatenate all speech chunks
    voiced_audio = torch.cat([wav[t['start']:t['end']] for t in speech_timestamps])

    # Save filtered audio
    voiced_audio_np = voiced_audio.numpy()
    sf.write(output_path, voiced_audio_np, sampling_rate)

    print(f"[Silero VAD] Saved speech-only audio to: {output_path}")
