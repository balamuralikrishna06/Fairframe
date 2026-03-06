from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from services.video_processor import VideoProcessor
from services.groq_service import GroqService
from services.sarvam_service import SarvamService
from services.supabase_service import SupabaseService
import tempfile
import os

router = APIRouter()
groq_service = GroqService()
sarvam_service = SarvamService()
supabase_service = SupabaseService()
video_processor = VideoProcessor(groq_service, sarvam_service)

@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...), x_user_id: str = Header(None)):
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_bytes = await file.read()

    import uuid
    tmp_path = os.path.join(tempfile.gettempdir(), f"upload_{uuid.uuid4().hex}.mp4")
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    try:
        result = await video_processor.process_video(tmp_path)

        media_url = None
        fallback_text = result.get("reasoning", "Video Analysis")
        
        if x_user_id:
            media_url = supabase_service.upload_file(file_bytes, file.filename or "video.mp4", file.content_type)
            supabase_service.save_analysis(
                x_user_id, "video", result, 
                media_url=media_url,
                input_content=fallback_text
            )

        return {**result, "media_url": media_url, "input_content": fallback_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
