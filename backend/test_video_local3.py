from utils.ffmpeg_utils import extract_frames_and_audio
import tempfile
import traceback

def test():
    # Make dummy video file again
    with open("dummy.mp4", "wb") as f:
        f.write(b'not a real video but need to check if ffmpeg runs without crashing with 4294967274')

    temp_dir = tempfile.mkdtemp()
    
    try:
        print("Testing extract_frames_and_audio...")
        frames, audio = extract_frames_and_audio("dummy.mp4", temp_dir)
        print("Success!", frames, audio)
    except Exception as e:
        print("EXCEPTION:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
