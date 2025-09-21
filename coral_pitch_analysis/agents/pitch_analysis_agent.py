"""
Pitch Analysis Agent using ElevenLabs Speech-to-Text
Transcribes pitch presentations from audio files (MP3).
"""

import os
import tempfile
import requests
import time
from typing import Optional, Union, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Try to import moviepy for video processing, fallback if not available
try:
    from moviepy import VideoFileClip
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

# Try to import Mistral analysis agent
try:
    from .mistral_analysis_agent import MistralAnalysisAgent
    HAS_MISTRAL = True
except ImportError:
    HAS_MISTRAL = False

# Try to import Voice agent
try:
    from .voice_agent import VoiceAgent
    HAS_VOICE = True
except ImportError:
    HAS_VOICE = False

# Load .env file
load_dotenv()

def retry_with_backoff(func, max_retries=3, initial_delay=1, backoff_factor=2, max_delay=60):
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Factor to multiply delay by after each retry
        max_delay: Maximum delay between retries

    Returns:
        Result of the function call
    """
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                raise e

            # Check if it's a rate limit error (429)
            if hasattr(e, 'status_code') and e.status_code == 429:
                delay = min(initial_delay * (backoff_factor ** attempt), max_delay)
                print(f"Rate limit exceeded. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                # For other errors, don't retry
                raise e

class PitchAnalysisAgent:
    """Agent for transcribing pitch presentations from audio files."""
    
    def __init__(self):
        """Initialize the pitch analysis agent."""
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY missing in .env file")
        
        self.client = ElevenLabs(api_key=self.api_key)

        # Initialize Mistral analysis agent (required)
        if not HAS_MISTRAL:
            raise ValueError("Mistral AI is required for pitch analysis. Please install mistralai package.")

        try:
            self.mistral_agent = MistralAnalysisAgent()
        except Exception as e:
            raise ValueError(f"Failed to initialize Mistral AI: {e}")

        # Initialize Voice agent (optional)
        if not HAS_VOICE:
            print("⚠️ Voice agent not available. Audio generation will be disabled.")
            self.voice_agent = None
        else:
            try:
                self.voice_agent = VoiceAgent()
                print("Voice agent initialized successfully!")
            except Exception as e:
                print(f"Failed to initialize voice agent: {e}")
                self.voice_agent = None

    def extract_audio_from_video(self, video_path: Union[str, Path]) -> Optional[str]:
        """
        Extract audio from video file and save as temporary MP3 file.

        Args:
            video_path (str or Path): Path to video file

        Returns:
            str or None: Path to extracted audio file, or None if extraction failed
        """
        if not HAS_MOVIEPY:
            print("❌ moviepy not installed. Cannot extract audio from video.")
            return None

        try:
            video_path = Path(video_path)
            if not video_path.exists():
                print(f"Video file not found: {video_path}")
                return None

            print(f"Extracting audio from video: {video_path}")

            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                temp_audio_path = temp_audio.name

            # Extract audio using moviepy
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(temp_audio_path)
            video.close()

            print(f"Audio extracted successfully to: {temp_audio_path}")
            return temp_audio_path

        except Exception as e:
            print(f"Error extracting audio from video: {e}")
            return None

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
                print(f"Downloading audio from URL: {file_path}")
                return self._transcribe_from_url(file_path, language_code)
            else:
                # Local file path
                file_path = Path(file_path)
                if not file_path.exists():
                    print(f"File not found: {file_path}")
                    return None

                print(f"Transcribing local audio file: {file_path}")
                return self._transcribe_local_file(file_path, language_code)

        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def _transcribe_from_url(self, url: str, language_code: str) -> Optional[str]:
        """Transcribe audio from URL."""
        def _transcribe_url():
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
                    print(f"Transcribing audio file...")
                    transcription = self.client.speech_to_text.convert(
                        file=audio_file,
                        model_id="scribe_v1",
                        tag_audio_events=False,
                        language_code=language_code,
                        diarize=True,
                    )

                    result = transcription.text.strip() if transcription.text.strip() else None
                    if result:
                        print(f"Transcription completed successfully!")
                    else:
                        print("No speech detected in the audio file.")
                    return result
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)

        try:
            return retry_with_backoff(_transcribe_url, max_retries=3, initial_delay=2)
        except requests.RequestException as e:
            print(f"Error downloading file from URL: {e}")
            return None
        except Exception as e:
            print(f"URL transcription error after retries: {e}")
            print("Note: This might be due to API rate limits or system overload.")

            # Provide helpful fallback information
            if hasattr(e, 'status_code') and e.status_code == 429:
                print("💡 Fallback: Consider downloading the file locally and using local file upload")
                return f"[TRANSCRIPTION UNAVAILABLE - API RATE LIMIT]\n\nUnable to transcribe audio from URL due to system overload. Please try again later or download the file and use local upload instead."
            else:
                return None
    
    def _transcribe_local_file(self, file_path: Path, language_code: str) -> Optional[str]:
        """Transcribe local audio file."""
        def _transcribe_file():
            with open(file_path, 'rb') as audio_file:
                print(f"Processing audio file...")
                transcription = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                    tag_audio_events=False,
                    language_code=language_code,
                    diarize=True,
                )

                result = transcription.text.strip() if transcription.text.strip() else None
                if result:
                    print(f"Transcription completed successfully!")
                else:
                    print("No speech detected in the audio file.")
                return result

        try:
            return retry_with_backoff(_transcribe_file, max_retries=3, initial_delay=2)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Transcription error after retries: {e}")
            print("Note: This might be due to API rate limits or system overload.")
            print("Consider trying again later or using a different audio file.")

            # Provide helpful fallback information
            if hasattr(e, 'status_code') and e.status_code == 429:
                print("💡 Fallback: Consider using text input mode if audio transcription continues to fail")
                return f"[TRANSCRIPTION UNAVAILABLE - API RATE LIMIT]\n\nUnable to transcribe audio due to system overload. Please try again later or use the text input option instead."
            else:
                return None
    
    def analyze_pitch(self, file_path: Union[str, Path], language_code: str = "eng") -> dict:
        """
        Transcribe a pitch presentation from an audio or video file.

        Args:
            file_path (str or Path): Path to audio/video file or URL
            language_code (str): Language code for transcription

        Returns:
            dict: Transcription results
        """
        print(f"Starting pitch transcription for: {file_path}")

        # Check if it's a video file
        file_extension = Path(file_path).suffix.lower()
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']

        audio_file_path = file_path
        temp_audio_file = None
        is_video = file_extension in video_extensions

        try:
            # If it's a video file, extract audio first
            if is_video:
                print(f"Detected video file: {file_extension}")
                temp_audio_file = self.extract_audio_from_video(file_path)
                if not temp_audio_file:
                    return {
                        "success": False,
                        "error": "Failed to extract audio from video file",
                        "transcription": None
                    }
                audio_file_path = temp_audio_file
                print(f"Using extracted audio file for transcription: {audio_file_path}")

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
                "file_path": str(file_path),
                "is_video": is_video
            }

        finally:
            # Clean up temporary audio file if it was created
            if temp_audio_file and os.path.exists(temp_audio_file):
                try:
                    os.unlink(temp_audio_file)
                    print(f"Cleaned up temporary audio file: {temp_audio_file}")
                except Exception as e:
                    print(f"Failed to clean up temporary file: {e}")

    def generate_comprehensive_analysis(self, pitch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive pitch analysis including Mistral AI evaluation.

        Args:
            pitch_data (dict): Complete pitch data including transcription and metadata

        Returns:
            dict: Analysis results with comprehensive evaluation
        """
        print("Starting comprehensive pitch analysis...")

        # First ensure we have transcription if it's audio/video
        if pitch_data.get('pitchType') in ['audio', 'video'] and 'pitch' not in pitch_data:
            # Get transcription first
            file_path = pitch_data.get('file')
            if file_path:
                transcription_result = self.analyze_pitch(file_path)
                if transcription_result['success']:
                    pitch_data['pitch'] = transcription_result['transcription']
                else:
                    return {
                        "success": False,
                        "error": "Failed to transcribe audio/video file",
                        "analysis": None
                    }

        # Generate Mistral AI analysis (required)
        try:
            print("Generating Mistral AI analysis...")
            mistral_result = self.mistral_agent.generate_comprehensive_analysis(pitch_data)

            if mistral_result['success']:
                analysis = mistral_result['analysis']

                # Generate audio for the AI response
                if self.voice_agent:
                    try:
                        audio_path = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads', f"ai_response_{analysis.get('id', 'unknown')}.mp3")
                        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
                        audio_success = self.generate_response_audio(analysis, audio_path)
                        if audio_success:
                            analysis['responseAudioPath'] = audio_path
                            print(f"✅ AI response audio generated: {audio_path}")
                        else:
                            print("⚠️ Failed to generate AI response audio")
                    except Exception as e:
                        print(f"⚠️ Error setting up audio generation: {e}")

                return {
                    "success": True,
                    "analysis": analysis,
                    "method": "mistral_ai"
                }
            else:
                raise ValueError(f"Mistral AI analysis failed: {mistral_result.get('error', 'Unknown error')}")

        except Exception as e:
            raise ValueError(f"Mistral AI analysis error: {e}")

    def generate_response_audio(self, analysis: Dict[str, Any], output_path: str) -> bool:
        """
        Generate audio narration for the AI response using ElevenLabs.

        Args:
            analysis (dict): The complete analysis result containing the AI response
            output_path (str): Path where the audio file should be saved

        Returns:
            bool: True if audio generation was successful, False otherwise
        """
        if not self.voice_agent:
            print("❌ Voice agent not available. Cannot generate audio.")
            return False

        # Extract the AI response from the analysis
        response_text = analysis.get('response', '')
        if not response_text:
            print("❌ No AI response found in analysis. Cannot generate audio.")
            return False

        try:
            print(f"🎵 Generating audio for AI response...")
            self.voice_agent.narrate_response(response_text, output_path)
            print(f"✅ AI response audio generated: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error generating response audio: {e}")
            return False



if __name__ == "__main__":
    # Test the agent
    agent = PitchAnalysisAgent()
    
    # Test with a sample (you would replace this with an actual file path or URL)
    print("Pitch Analysis Agent Test")
    print("-" * 40)
    print("To test the agent, provide an audio file path or URL:")
    print("result = agent.analyze_pitch('path/to/your/pitch.mp3')")
    print("print(result)")
