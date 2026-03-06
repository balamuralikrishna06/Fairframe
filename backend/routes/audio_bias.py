from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from services.groq_service import GroqService
from services.sarvam_service import SarvamService
from services.supabase_service import SupabaseService
import tempfile
import os

router = APIRouter()
groq_service = GroqService()
sarvam_service = SarvamService()
supabase_service = SupabaseService()

@router.post("/analyze")
async def analyze_audio(file: UploadFile = File(...), x_user_id: str = Header(None)):
    if not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_bytes = await file.read()

    import uuid
    tmp_path = os.path.join(tempfile.gettempdir(), f"upload_{uuid.uuid4().hex}.wav")
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    try:
        transcript = await groq_service.transcribe_audio(tmp_path)
        if not transcript:
            raise HTTPException(status_code=500, detail="Transcription failed. No text returned.")

        result = await groq_service.analyze_text_bias(transcript)

        media_url = None
        if x_user_id:
            media_url = supabase_service.upload_file(file_bytes, file.filename or "audio.wav", file.content_type)
            supabase_service.save_analysis(x_user_id, "audio", result,
                                           input_content=transcript, media_url=media_url)

        return {**result, "media_url": media_url, "input_content": transcript}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Audio analysis error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
