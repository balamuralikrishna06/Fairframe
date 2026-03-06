BIAS_ANALYSIS_PROMPT = """
Analyze the following content and detect bias.

Return ONLY JSON.

{
"bias_score": number,
"bias_detected": true/false,
"bias_type": [],
"biased_phrases": [],
"cause_of_bias": "",
"explanation": "",
"suggestion_to_fix": ""
}

Rules:
• Detect both explicit and implicit bias
• Identify specific phrases that cause bias
• Provide neutral alternative wording
• If no bias exists return bias_score below 20
• Avoid hallucination
• Be objective and factual

Content to analyze:
{content}
"""

IMAGE_CAPTION_PROMPT = """
Describe the following image in detail, focusing on the people, actions, and context. 
Your description will be used to analyze potential bias, so be as objective and descriptive as possible.
"""

VIDEO_FRAME_CAPTION_PROMPT = """
Describe this frame from a video. Focus on characters, their expressions, and the overall scene context.
"""
