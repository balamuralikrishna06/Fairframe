"""
Directly test extract_frames_and_audio with a real video to diagnose the issue.
"""
import tempfile
import shutil
import sys
import os

sys.path.insert(0, ".")

from utils.ffmpeg_utils import p, extract_frames_and_audio

video = "real_test.mp4"
temp_dir = tempfile.mkdtemp()

print(f"video_path raw: {repr(video)}")
print(f"video_path abs: {repr(os.path.abspath(video))}")
print(f"output_dir raw: {repr(temp_dir)}")
print(f"output_dir posix: {repr(p(temp_dir))}")

audio_path = p(temp_dir) + "/audio.wav"
print(f"audio_path: {repr(audio_path)}")

# Try directly
import subprocess
vp = p(video)
cmd = f'ffmpeg -y -i "{vp}" -t 5 -vn -acodec pcm_s16le -ar 16000 -ac 1 "{audio_path}"'
print(f"\nRunning: {cmd}\n")
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("returncode:", result.returncode)
print("stdout:", result.stdout[-300:])
print("stderr:", result.stderr[-500:])

shutil.rmtree(temp_dir)
