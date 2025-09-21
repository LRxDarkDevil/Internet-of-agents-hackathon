"""
Pitch Analysis Agent using ElevenLabs Speech-to-Text
Transcribes pitch presentations from audio files (MP3).
"""

import os
import tempfile
import requests
from typing import Optional, Union
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load .env file
load_dotenv()

class PitchAnalysisAgent:
    """Agent for transcribing pitch presentations from audio files."""
    
    def __init__(self):
        """Initialize the pitch analysis agent."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY missing in .env file")
        
        self.client = ElevenLabs(api_key=self.api_key)
    
    def transcribe_audio_file(self, file_path: Union[str, Path], language_code: str = "eng") -> Optional[str]:
        """
        Transcribe audio file to text using ElevenLabs.
        Supports both local files and web URLs.

        Args:
            file_path (str or Path): Path to local audio file or URL to audio file
            language_code (str): Language code for transcription (default: "eng")

        Returns:
            str or None: Transcribed text, or None if error occurred
        """
        try:
            # Check if it's a URL or local file
            if str(file_path).startswith(('http://', 'https://')):
                print(f"🌐 Downloading audio from URL: {file_path}")
                return self._transcribe_from_url(file_path, language_code)
            else:
                # Local file path
                file_path = Path(file_path)
                if not file_path.exists():
                    print(f"❌ File not found: {file_path}")
                    return None

                print(f"📁 Transcribing local audio file: {file_path}")
                return self._transcribe_local_file(file_path, language_code)

        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def _transcribe_from_url(self, url: str, language_code: str) -> Optional[str]:
        """Transcribe audio from URL."""
        try:
            # Download the file from URL
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            try:
                # Transcribe the temporary file
                with open(temp_file_path, 'rb') as audio_file:
                    print(f"🎵 Transcribing audio file...")
                    transcription = self.client.speech_to_text.convert(
                        file=audio_file,
                        model_id="scribe_v1",
                        tag_audio_events=False,
                        language_code=language_code,
                        diarize=True,
                    )

                    result = transcription.text.strip() if transcription.text.strip() else None
                    if result:
                        print(f"✅ Transcription completed successfully!")
                    else:
                        print("⚠️ No speech detected in the audio file.")
                    return result
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        except requests.RequestException as e:
            print(f"❌ Error downloading file from URL: {e}")
            return None
    
    def _transcribe_local_file(self, file_path: Path, language_code: str) -> Optional[str]:
        """Transcribe local audio file."""
        try:
            with open(file_path, 'rb') as audio_file:
                print(f"🎵 Processing audio file...")
                transcription = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                    tag_audio_events=False,
                    language_code=language_code,
                    diarize=True,
                )

                result = transcription.text.strip() if transcription.text.strip() else None
                if result:
                    print(f"✅ Transcription completed successfully!")
                else:
                    print("⚠️ No speech detected in the audio file.")
                return result

        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def analyze_pitch(self, audio_file_path: Union[str, Path], language_code: str = "eng") -> dict:
        """
        Transcribe a pitch presentation from an audio file.
        
        Args:
            audio_file_path (str or Path): Path to audio file or URL
            language_code (str): Language code for transcription
            
        Returns:
            dict: Transcription results
        """
        print(f"🎯 Starting pitch transcription for: {audio_file_path}")
        
        # Transcribe the audio
        transcription = self.transcribe_audio_file(audio_file_path, language_code)
        
        if not transcription:
            return {
                "success": False,
                "error": "Failed to transcribe audio file",
                "transcription": None
            }
        
        return {
            "success": True,
            "transcription": transcription,
            "file_path": str(audio_file_path)
        }


if __name__ == "__main__":
    # Test the agent
    agent = PitchAnalysisAgent()
    
    # Test with a sample (you would replace this with an actual file path or URL)
    print("🎯 Pitch Analysis Agent Test")
    print("-" * 40)
    print("To test the agent, provide an audio file path or URL:")
    print("result = agent.analyze_pitch('path/to/your/pitch.mp3')")
    print("print(result)")
