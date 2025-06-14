import soundfile as sf
import numpy as np
import rnnoise_wrapper

def run_rnnoise(input_path, output_path):
    audio, sr = sf.read(input_path)
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)  # Mono mixdown

    denoised = []
    frame_size = 480  # 30ms at 16kHz
    model = rnnoise_wrapper.RNNoise()
    for i in range(0, len(audio), frame_size):
        frame = audio[i:i+frame_size]
        if len(frame) < frame_size:
            frame = np.pad(frame, (0, frame_size - len(frame)))
        denoised.append(model.filter(frame))

    denoised_audio = np.concatenate(denoised)
    sf.write(output_path, denoised_audio, sr)