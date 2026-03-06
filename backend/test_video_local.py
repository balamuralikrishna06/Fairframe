import asyncio
from services.video_processor import VideoProcessor
from services.groq_service import GroqService
from services.sarvam_service import SarvamService
import traceback

async def test():
    gs = GroqService()
    ss = SarvamService()
    vp = VideoProcessor(gs, ss)

    with open("dummy.mp4", "wb") as f:
        # A tiny valid mp4 header or you'd just get an 'invalid data' from ffmpeg, but that's what we want to test anyway (if ffmpeg can run)
        f.write(b'this is not a real video but ffmpeg should complain about format, not crash with 4294967274')

    try:
        await vp.process_video("dummy.mp4")
    except Exception as e:
        print("EXCEPTION: ")
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
