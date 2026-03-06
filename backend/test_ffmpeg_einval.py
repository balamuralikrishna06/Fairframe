import subprocess
import tempfile
import traceback
import os

def test():
    # Write a tiny valid mp4 using base64
    import base64
    small_video = base64.b64decode("AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAAIZnJlZQAACsBtZGF0AAACrgYF//+//7H/wA2PwhIhiAAAAABlW/u1cQAAYx1t0//A9mXQhAQAAAARAAAARAAAP/////+b9X7////4sAAAEAAAASAAAAx+5u290AAAMrYmSGAgAAAAcAAAAOAAAA7gAAAPwAAQMAAAMrAAAFK21vb3YAAABsbXZoZAAAAAAAAAAAAAAAAAAAA+gAAAAAAAEAAAEAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAABpdHJhawAAAFx0a2hkAAAAMwAAAAAAAAAAAAAAAQAAAAAAAAPoAAAAAAAAAAAAAAAAAQAAAAABAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAQAAAAAEAAAAAAQAAAAAAJGVkdHMAAAAcZWxzdAAAAAAAAAABAAAD6AAAAAAAQAAAAAAANW1kaWEAAAAgbWRoZAAAAAAAAAAAAAAAAAAADhAAAA4QVxAAAAAAACxoZGxyAAAAAAAAAAB2aWRlAAAAAAAAAAAAAAAAVmlkZW9IYW5kbGVyAAAA2m1pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAv3N0YmwAAACLc3RzZAAAAAAAAAABAAAAe2F2YzEAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAABAAEASAAAAEgAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABj//wAAADhhdmNDAWQAZv/hABhnZABm1tJAJbwHBAADCAAAAAMAgSAAEAFXwB1qxgEDAwgAAAMAAAMHAAAQAAAABHN0dHMAAAAAAAAAAQAAAAMAAABzAAAAFHN0c3MAAAAAAAAAAQAAAAEAAAAYc3RzYwAAAAAAAAABAAAAAQAAAAMAAAABAAAAHHN0c3oAAAAAAAAAAAAAAAMAAAQfAAAAqAAAAK0AAAAUc3RjbwAAAAAAAAABAAAAMAAAADJ1ZHRhAAAAKm1ldGEAAAAAAAAAIWhkbHIAAAAAAAAAAG1kaXJhcHBsAAAAAAAAAAAAAAAA")
    video_path = "test_valid.mp4"
    with open(video_path, "wb") as f:
        f.write(small_video)

    out_dir = tempfile.mkdtemp()
    audio_path = os.path.join(out_dir, "audio.wav")
    
    print("Testing output to:", audio_path)
    audio_cmd = ["ffmpeg", "-i", video_path, "-t", "30", "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path, "-y"]
    try:
        subprocess.run(audio_cmd, check=True)
        print("Success 1!")
    except subprocess.CalledProcessError as e:
        print("Failed 1! Code:", e.returncode)
    
    # Try with forward slashes
    audio_path2 = audio_path.replace("\\", "/")
    print("Testing output to (forward slashes):", audio_path2)
    audio_cmd2 = ["ffmpeg", "-i", video_path, "-t", "30", "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path2, "-y"]
    try:
        subprocess.run(audio_cmd2, check=True)
        print("Success 2!")
    except subprocess.CalledProcessError as e:
        print("Failed 2! Code:", e.returncode)

if __name__ == "__main__":
    test()
