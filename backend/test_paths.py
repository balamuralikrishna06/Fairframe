import tempfile, os, subprocess

d = tempfile.mkdtemp()
dp = d.replace('\\', '/')
ap = dp + '/audio.wav'

print("raw:", repr(d))
print("posix dir:", dp)
print("audio path:", ap)

cmd = f'ffmpeg -y -f lavfi -i aevalsrc=0:c=mono:r=16000 -t 1 "{ap}"'
print("cmd:", cmd)
r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("returncode:", r.returncode)
print("stderr (last 400 chars):", r.stderr[-400:])
