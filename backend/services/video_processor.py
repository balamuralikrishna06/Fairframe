from services.groq_service import GroqService
from services.sarvam_service import SarvamService
from utils.ffmpeg_utils import extract_frames_and_audio
import os
import shutil
import tempfile

class VideoProcessor:
    def __init__(self, groq_service: GroqService, sarvam_service: SarvamService):
        self.groq_service = groq_service
        self.sarvam_service = sarvam_service

    async def process_video(self, video_path: str):
        temp_dir = tempfile.mkdtemp()
        try:
            frame_paths, audio_path = extract_frames_and_audio(video_path, temp_dir)

            # 1. Transcribe audio
            transcript = await self.groq_service.transcribe_audio(audio_path) if audio_path else ""

            # 2. Load frame bytes (max 3)
            frames_data = []
            for path in frame_paths[:3]:
                with open(path, "rb") as f:
                    frames_data.append(f.read())

            # 3. Single multimodal call: frames + transcript together
            result = await self.groq_service.analyze_video_frames(frames_data, transcript or "")

            return result

        finally:
            shutil.rmtree(temp_dir)
