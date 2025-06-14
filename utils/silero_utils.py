import torchaudio
import torch
import numpy as np
import soundfile as sf
from silero_vad import VoiceActivityDetector
import os

def run_silero_vad(input_path: str, output_path: str, threshold: float = 0.5):
    """
    Applies Silero Voice Activity Detection (VAD) to an input audio file.
    Removes non-speech regions and writes the cleaned audio to output_path.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Where to save the VAD-filtered audio.
        threshold (float): Threshold for speech probability (default is 0.5).
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Load audio with torchaudio (supports many formats)
    wav, sr = torchaudio.load(input_path)

    # Ensure mono audio
    if wav.shape[0] > 1:
        wav = wav.mean(dim=0, keepdim=True)

    # Initialize Silero VAD (on CPU)
    vad = VoiceActivityDetector("cpu")

    # Run VAD and get per-frame speech probabilities
    with torch.no_grad():
        speech_probs = vad(wav, sampling_rate=sr)

    # Select frames above threshold
    keep = (speech_probs[0] > threshold).numpy()

    if not keep.any():
        raise ValueError("No speech detected with the given threshold.")

    # Filter audio
    voiced_audio = wav[:, keep].squeeze().numpy()

    # Save filtered audio
    sf.write(output_path, voiced_audio, sr)

    print(f"[Silero VAD] Saved speech-only audio to: {output_path}")
