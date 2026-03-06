import asyncio
from services.video_processor import VideoProcessor
from services.groq_service import GroqService
from services.sarvam_service import SarvamService
import traceback
import tempfile

async def test():
    gs = GroqService()
    ss = SarvamService()
    vp = VideoProcessor(gs, ss)

    # Let's test standard tempfile handling on Windows
    # Option 1: Like currently implemented (inside with block)
    print("Testing standard 'with' block behavior...")
    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(b'this is not a real video but ffmpeg should complain about format, not crash with 4294967274')
            tmp_path = tmp.name
            
            # This simulates what currently happens in video_bias.py BEFORE the with block exits
            # Wait, in video_bias.py the with block EXITS BEFORE video_processor is called!
            print("Is file closed during with?", tmp.closed)

        print("Is file closed after with?", tmp.closed)

        await vp.process_video(tmp_path)
    except Exception as e:
        print("EXCEPTION: ")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
