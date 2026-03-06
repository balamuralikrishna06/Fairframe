import subprocess
import os
import tempfile
import uuid

def p(path: str) -> str:
    """Normalize a path to use forward slashes for ffmpeg compatibility on Windows."""
    return os.path.abspath(path).replace("\\", "/")

def has_audio_stream(video_path: str) -> bool:
    """Check if a video has an audio stream using ffprobe."""
    vp = p(video_path)
    cmd = f'ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of default=noprint_wrappers=1:nokey=1 "{vp}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip() == "audio"

def extract_frames_and_audio(video_path: str, output_dir: str):
    """
    Extracts 3 frames (start, middle, end) and audio from video.
    Returns paths to extracted files.
    Audio may be None if the video has no audio stream.
    """
    vp = p(video_path)
    od = p(output_dir)

    # Get duration
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{vp}"'
    result = subprocess.run(duration_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed:\n{result.stderr}")
    duration = float(result.stdout.strip())

    # Extract audio only if there is an audio stream
    audio_path = None
    if has_audio_stream(video_path):
        audio_path = os.path.join(output_dir, "audio.wav")
        ap = od + "/audio.wav"
        audio_cmd = f'ffmpeg -y -i "{vp}" -t 30 -vn -acodec pcm_s16le -ar 16000 -ac 1 "{ap}"'
        result = subprocess.run(audio_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[WARN] ffmpeg audio extraction failed, skipping audio.\n{result.stderr[-500:]}")
            audio_path = None

    # Extract 3 frames - cap times to 90% of duration to avoid seeking past end
    frame_paths = []
    max_t = duration * 0.90
    raw_times = [0, duration / 2, max_t]
    times = [min(t, max_t) for t in raw_times]

    for i, t in enumerate(times):
        fp = od + f"/frame_{i}.jpg"
        frame_cmd = f'ffmpeg -y -ss {t} -i "{vp}" -vframes 1 -q:v 2 -vf format=yuvj420p "{fp}"'
        result = subprocess.run(frame_cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(fp):
            print(f"[WARN] Frame {i} at t={t:.2f}s failed or empty, skipping.\n{result.stderr[-200:]}")
            continue
        frame_paths.append(fp)

    if not frame_paths:
        raise RuntimeError("Failed to extract any frames from the video.")

    return frame_paths, audio_path
