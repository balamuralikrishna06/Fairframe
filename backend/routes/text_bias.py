from fastapi import APIRouter, HTTPException
from services.groq_service import GroqService
from services.supabase_service import SupabaseService
from pydantic import BaseModel

router = APIRouter()
groq_service = GroqService()
supabase_service = SupabaseService()

class TextAnalysisRequest(BaseModel):
    text: str
    user_id: str

@router.post("/analyze")
async def analyze_text(request: TextAnalysisRequest):
    try:
        result = await groq_service.analyze_text_bias(request.text)
        supabase_service.save_analysis(request.user_id, "text", result, input_content=request.text)
        return {**result, "input_content": request.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
