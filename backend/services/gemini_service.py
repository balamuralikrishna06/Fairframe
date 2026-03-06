import os
from dotenv import load_dotenv
load_dotenv()
from google import genai
from google.genai import types
from typing import Dict, Any, List
import json
from utils.prompts import BIAS_ANALYSIS_PROMPT, IMAGE_CAPTION_PROMPT, VIDEO_FRAME_CAPTION_PROMPT

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.0-flash-lite'

    async def analyze_bias(self, content: str) -> Dict[str, Any]:
        """Analyzes text content for bias."""
        prompt = BIAS_ANALYSIS_PROMPT.format(content=content)
        response = self.client.models.generate_content(model=self.model_name, contents=prompt)
        return self._parse_json(response.text)

    async def analyze_image_bias(self, image_data: bytes) -> Dict[str, Any]:
        """Analyzes an image directly for bias using multi-modal capabilities."""
        prompt = BIAS_ANALYSIS_PROMPT.format(content="[IMAGE_DATA]")
        image_part = types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, image_part]
        )
        return self._parse_json(response.text)

    async def generate_caption(self, image_data: bytes, prompt: str = IMAGE_CAPTION_PROMPT) -> str:
        """Generates a descriptive caption for an image."""
        image_part = types.Part.from_bytes(data=image_data, mime_type="image/jpeg")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, image_part]
        )
        return response.text

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            json_str = text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return {
                "bias_score": 0,
                "bias_detected": False,
                "bias_type": [],
                "biased_phrases": [],
                "cause_of_bias": "Error processing response",
                "explanation": "Failed to parse AI response. Raw: " + text[:100],
                "suggestion_to_fix": ""
            }

    async def analyze_video_frames(self, frames: List[bytes]) -> List[str]:
        """Generates captions for a list of frames."""
        captions = []
        for frame in frames:
            caption = await self.generate_caption(frame, prompt=VIDEO_FRAME_CAPTION_PROMPT)
            captions.append(caption)
        return captions
