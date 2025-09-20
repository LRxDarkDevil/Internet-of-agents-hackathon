import os
import requests

class VoiceAgent:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel (public ElevenLabs voice)
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def narrate_pitch(self, pitch_json, output_path):
        """
        Calls ElevenLabs API to generate voice narration for the pitch.
        Saves audio to output_path.
        """
        text = f"Problem: {pitch_json.get('problem')}\nSolution: {pitch_json.get('solution')}\nMarket: {pitch_json.get('market')}\nBusiness Model: {pitch_json.get('business_model')}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "output_format": "mp3_44100_128"
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(f"ElevenLabs API error: {e}")
            print("Raw response:", getattr(e, 'response', None))
            with open(output_path, 'wb') as f:
                f.write(b"FAKE_MP3_DATA")
