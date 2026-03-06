import tempfile, os, subprocess, shutil

# Test writing audio to a known safe path (no temp dir with \t in it)
os.makedirs("tmp_ffmpeg_test", exist_ok=True)
ap = os.path.abspath("tmp_ffmpeg_test/audio.wav").replace("\\", "/")
vp = os.path.abspath("real_test.mp4").replace("\\", "/")

print("video path:", vp)
print("audio path:", ap)

cmd = f'ffmpeg -y -i "{vp}" -t 5 -vn -acodec pcm_s16le -ar 16000 -ac 1 "{ap}"'
print("running:", cmd[:100])
r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("returncode:", r.returncode)
print("stderr:", r.stderr[-300:])
if r.returncode == 0:
    print("SUCCESS! audio file size:", os.path.getsize(ap))
shutil.rmtree("tmp_ffmpeg_test", ignore_errors=True)
