import os
import requests
from typing import Optional

class SarvamService:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.base_url = "https://api.sarvam.ai/speech-to-text" # Placeholder, actual URL needed

    async def transcribe(self, audio_path: str) -> Optional[str]:
        if not self.api_key:
            print("SARVAM_API_KEY not set")
            return None
        
        try:
            with open(audio_path, 'rb') as f:
                files = {'file': f}
                headers = {'api-key': self.api_key}
                response = requests.post(self.base_url, files=files, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("transcript")
        except Exception as e:
            print(f"Sarvam Transcription error: {e}")
            return None
