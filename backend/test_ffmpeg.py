import subprocess
try:
    print("Testing ffmpeg:")
    subprocess.run("ffmpeg -version", shell=True, check=True)
    print("\nTesting ffprobe:")
    subprocess.run("ffprobe -version", shell=True, check=True)
except Exception as e:
    print(f"Error testing ffmpeg/ffprobe: {e}")
