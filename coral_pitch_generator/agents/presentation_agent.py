import os
import requests

class PresentationAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    def format_pitch(self, pitch_json):
        """
        Uses Mistral API to reformat pitch JSON into a presentable summary (bulleted, slide-style, or paragraph).
        Returns formatted string.
        """
        prompt = (
            "Take the following startup pitch JSON and rewrite it as a concise, engaging pitch deck slide. "
            "Use bullet points and clear section headings.\n\n"
            f"Pitch JSON:\n{pitch_json}\n\nFormatted Slide:"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-tiny",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            formatted = result["choices"][0]["message"]["content"]
            return formatted
        except Exception as e:
            print(f"Mistral Presentation API error: {e}")
            return "Could not format pitch."
