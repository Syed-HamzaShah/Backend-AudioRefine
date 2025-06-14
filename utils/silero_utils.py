import torchaudio
import torch
import numpy as np
import soundfile as sf
from silero_vad import VoiceActivityDetector

def run_silero_vad(input_path, output_path):
    wav, sr = torchaudio.load(input_path)
    vad = VoiceActivityDetector("cpu")
    speech_probs = vad(wav, sampling_rate=sr)
    
    threshold = 0.5
    keep = speech_probs[0] > threshold
    keep = keep.numpy()
    
    # Apply mask
    voiced_audio = wav[:, keep].numpy()[0]
    sf.write(output_path, voiced_audio, sr)