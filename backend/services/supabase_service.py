import os
import uuid
from supabase import create_client, Client
from datetime import datetime

class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or "your_supabase_url" in url or not key or "your_supabase_service_role" in key:
            print("Warning: Valid SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found. Database storage will be disabled.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(url, key)
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
                self.client = None

    def upload_file(self, file_bytes: bytes, filename: str, content_type: str) -> str | None:
        """Upload a file to the fairframe bucket and return its public URL."""
        if not self.client:
            return None
        try:
            unique_name = f"{uuid.uuid4()}_{filename}"
            self.client.storage.from_("fairframe").upload(
                path=unique_name,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            public_url = self.client.storage.from_("fairframe").get_public_url(unique_name)
            return public_url
        except Exception as e:
            print(f"Supabase storage upload error: {e}")
            return None

    def save_analysis(self, user_id: str, input_type: str, analysis_result: dict,
                      input_content: str = None, media_url: str = None):
        if not self.client:
            return None

        # Support both old Gemini format and new Groq format
        rectification = analysis_result.get("rectification_plan") or {}
        visual_findings = analysis_result.get("visual_findings")
        linguistic_findings = analysis_result.get("linguistic_findings")

        data = {
            "user_id": user_id,
            "input_type": input_type,
            "input_content": input_content or "",
            "media_url": media_url or "",
            "overall_bias_score": (
                analysis_result.get("overall_bias_score") or
                analysis_result.get("bias_score") or 0
            ),
            "reasoning": (
                analysis_result.get("reasoning") or
                analysis_result.get("explanation") or ""
            ),
            "visual_findings": visual_findings if isinstance(visual_findings, list) else [],
            "linguistic_findings": linguistic_findings if isinstance(linguistic_findings, list) else [],
            "text_fix": rectification.get("text_fix") or analysis_result.get("suggestion_to_fix") or "",
            "visual_fix": rectification.get("visual_fix") or "",
            "created_at": datetime.now().isoformat()
        }

        try:
            res = self.client.table("analysis").insert(data).execute()
            return res.data[0]["id"] if res.data else None
        except Exception as e:
            print(f"Supabase error: {e}")
            return None

    def get_history(self, user_id: str):
        if not self.client:
            return []
        try:
            res = self.client.table("analysis")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(50)\
                .execute()
            return res.data or []
        except Exception as e:
            print(f"Supabase history fetch error: {e}")
            return []
