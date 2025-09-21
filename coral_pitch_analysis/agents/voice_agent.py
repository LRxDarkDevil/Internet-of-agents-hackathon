import os
import requests

class VoiceAgent:
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel (public ElevenLabs voice)
        self.api_url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    def narrate_response(self, response_text, output_path):
        """
        Calls ElevenLabs API to generate voice narration for the AI response.
        Saves audio to output_path.

        Args:
            response_text (str): The AI response text to convert to speech
            output_path (str): Path where the audio file should be saved
        """
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": response_text,
            "model_id": "eleven_multilingual_v2",
            "output_format": "mp3_44100_128"
        }
        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"AI response audio generated successfully: {output_path}")
        except Exception as e:
            print(f"ElevenLabs API error: {e}")
            print("Raw response:", getattr(response, 'text', 'No response text'))
            # Create a placeholder file to prevent UI errors
            with open(output_path, 'wb') as f:
                f.write(b"FAKE_MP3_DATA")


if __name__ == "__main__":
    # Test the voice agent
    agent = VoiceAgent()
    test_response = "This pitch demonstrates strong potential with clear value proposition. Consider emphasizing the competitive advantages and market timing more prominently."
    agent.narrate_response(test_response, "test_response.mp3")
    print("Voice agent test completed!")