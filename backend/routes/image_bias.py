from fastapi import APIRouter, UploadFile, File, HTTPException, Header
from services.groq_service import GroqService
from services.supabase_service import SupabaseService

router = APIRouter()
groq_service = GroqService()
supabase_service = SupabaseService()

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...), x_user_id: str = Header(None)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        contents = await file.read()

        # Generate caption first, then analyze for bias
        caption = await groq_service.generate_caption(contents)
        result = await groq_service.analyze_image_bias(contents)

        media_url = None
        if x_user_id:
            media_url = supabase_service.upload_file(contents, file.filename or "image.jpg", file.content_type)
            supabase_service.save_analysis(
                x_user_id, "image", result,
                input_content=caption,
                media_url=media_url
            )

        return {**result, "media_url": media_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
