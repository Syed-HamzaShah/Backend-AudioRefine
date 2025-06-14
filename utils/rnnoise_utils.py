import soundfile as sf
import numpy as np
import rnnoise_wrapper
import os

def run_rnnoise(input_path: str, output_path: str):
    """
    Applies RNNoise to reduce noise from the input audio and saves the result.
    - Converts stereo to mono if needed.
    - Pads incomplete frames.
    - Handles errors gracefully.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    try:
        audio, sr = sf.read(input_path)
    except Exception as e:
        raise RuntimeError(f"Failed to read input audio: {e}")

    # Ensure sampling rate is 16kHz (as RNNoise is optimized for 16kHz)
    if sr != 16000:
        raise ValueError("RNNoise requires 16kHz input audio. Please resample before processing.")

    # Mono mixdown if stereo
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    denoised = []
    frame_size = 480  # RNNoise expects 480-sample frames (30ms @ 16kHz)
    model = rnnoise_wrapper.RNNoise()

    for i in range(0, len(audio), frame_size):
        frame = audio[i:i+frame_size]
        if len(frame) < frame_size:
            frame = np.pad(frame, (0, frame_size - len(frame)))
        try:
            filtered = model.filter(frame)
            denoised.append(filtered)
        except Exception as e:
            raise RuntimeError(f"RNNoise filtering error at frame {i//frame_size}: {e}")

    denoised_audio = np.concatenate(denoised)

    try:
        sf.write(output_path, denoised_audio, sr)
    except Exception as e:
        raise RuntimeError(f"Failed to write output audio: {e}")
