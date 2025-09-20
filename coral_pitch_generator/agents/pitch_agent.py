import os
import requests
import json

class PitchAgent:
    def __init__(self):
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.api_url = "https://api.mistral.ai/v1/chat/completions"

    def generate_pitch(self, topic):
        """
        Calls Mistral API to generate a startup pitch for the given topic.
        Returns: dict with keys: problem, solution, market, business_model
        """
        prompt = f"Generate a startup pitch for the domain: {topic}. Return JSON with keys: problem, solution, market, business_model."
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            try:
                result = response.json()
            except Exception as json_err:
                print("Mistral API raw response:", response.text)
                raise json_err
            pitch_text = result.get('choices', [{}])[0].get('message', {}).get('content', '{}')
            import re
            # Extract JSON from Markdown code block if present
            match = re.search(r'```json\s*(\{.*?\})\s*```', pitch_text, re.DOTALL)
            if match:
                pitch_text_clean = match.group(1)
            else:
                pitch_text_clean = pitch_text
            try:
                pitch_json = json.loads(pitch_text_clean)
            except Exception as parse_err:
                print("Mistral API pitch text:", pitch_text_clean)
                raise parse_err
            return pitch_json
        except Exception as e:
            print(f"Mistral API error: {e}")
            return {
                "problem": f"Problem for {topic}",
                "solution": f"Solution for {topic}",
                "market": "Market size and opportunity",
                "business_model": "Business model details"
            }


if __name__ == "__main__":
    agent = PitchAgent()
    result = agent.generate_pitch("AI in healthcare")
    print(json.dumps(result, indent=2))
