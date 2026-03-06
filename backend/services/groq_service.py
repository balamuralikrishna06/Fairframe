import os
import base64
import json
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from typing import Dict, Any, List

MASTER_PROMPT = """You are a "Multimodal Bias Auditor." Your goal is to analyze provided text, audio transcripts, and visual frames for gender bias, stereotypes, or exclusionary language. You must provide a quantitative score and actionable rectification steps.

Task:
- Analyze Visuals: Identify gender-coded colors, stereotypical roles (e.g., only men in tech), or lack of diversity.
- Analyze Text/Audio: Flag biased terminology (e.g., "manpower" instead of "workforce") or gender-weighted assumptions.

Output Format: You MUST return a valid JSON object. Do not include any conversational text.

JSON Schema:
{
  "overall_bias_score": (int 0-100),
  "visual_findings": ["list of specific visual biases found"],
  "linguistic_findings": ["list of biases found in text/audio"],
  "reasoning": "A concise explanation of the final score",
  "rectification_plan": {
    "text_fix": "suggested neutral rewrite",
    "visual_fix": "suggested changes for image/video composition"
  }
}"""


class GroqService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"  # Groq's current vision model
        self.text_model = "llama-3.3-70b-versatile"  # best general text model on Groq

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            json_str = text.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        except Exception as e:
            print(f"Error parsing Groq response: {e}\nRaw: {text[:200]}")
            return {
                "overall_bias_score": 0,
                "visual_findings": [],
                "linguistic_findings": [],
                "reasoning": "Failed to parse AI response.",
                "rectification_plan": {"text_fix": "", "visual_fix": ""}
            }

    async def analyze_text_bias(self, text: str) -> Dict[str, Any]:
        """Analyze text content for bias."""
        response = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": MASTER_PROMPT},
                {"role": "user", "content": f"Analyze this text for bias:\n\n{text}"}
            ],
            response_format={"type": "json_object"}
        )
        return self._parse_json(response.choices[0].message.content)

    async def analyze_image_bias(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze an image for bias using vision model."""
        b64 = base64.b64encode(image_data).decode('utf-8')
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": MASTER_PROMPT + "\n\nAnalyze this image for gender bias and stereotypes."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return self._parse_json(response.choices[0].message.content)

    async def generate_caption(self, image_data: bytes) -> str:
        """Generate a description of an image."""
        b64 = base64.b64encode(image_data).decode('utf-8')
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail, focusing on people, their roles, activities, and any visual elements that could relate to gender representation."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    async def analyze_video_frames(self, frames: List[bytes], transcript: str = "") -> Dict[str, Any]:
        """Analyze video frames + transcript for bias (multimodal)."""
        images_content = []
        for frame_data in frames[:3]:  # max 3 frames (model limit)
            b64 = base64.b64encode(frame_data).decode('utf-8')
            images_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
            })

        combined_text = f"Audio Transcript: {transcript}" if transcript else "No audio transcript available."

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": MASTER_PROMPT},
                        {"type": "text", "text": f"Analyze these video frames and transcript for bias.\n\n{combined_text}"},
                        *images_content
                    ]
                }
            ],
            response_format={"type": "json_object"}
        )
        return self._parse_json(response.choices[0].message.content)

    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Groq's Whisper model (whisper-large-v3-turbo)."""
        try:
            with open(audio_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), file.read()),
                    model="whisper-large-v3-turbo",
                )
                return transcription.text
        except Exception as e:
            print(f"Groq transcription error: {e}")
            raise Exception(f"Groq API Error: {str(e)}")
