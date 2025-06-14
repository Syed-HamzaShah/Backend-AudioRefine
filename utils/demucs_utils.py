import subprocess
import os

def run_demucs(input_path):
    cmd = f"demucs \"{input_path}\""
    subprocess.run(cmd, shell=True)