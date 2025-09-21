# Coral Pitch Analysis

A speech-to-text tool that transcribes audio and video pitch presentations using ElevenLabs.

## Features

- 🎵 **Audio Transcription**: Convert audio files (MP3, WAV, M4A, OGG) to text using ElevenLabs
- 🎬 **Video Transcription**: Extract audio from video files (MP4, AVI, MOV, MKV) and transcribe using ElevenLabs
-  **URL Support**: Transcribe audio/video files from URLs or local uploads
- 📱 **Streamlit Interface**: Easy-to-use web interface for testing
- 📊 **Basic Statistics**: Word count and character count

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

3. Run the Streamlit test interface:
```bash
streamlit run pitch_analysis_test.py
```

## Usage

### Using the Streamlit Interface

1. Open the web interface
2. Choose to upload a file or provide a URL
3. Click "Transcribe Pitch"
4. View transcription results
5. Download results as JSON

### Supported file formats:
- **Audio**: MP3, WAV, M4A, OGG
- **Video**: MP4, AVI, MOV, MKV (audio extraction + transcription)

### Using the Agent Directly

```python
from agents.pitch_analysis_agent import PitchAnalysisAgent

# Initialize agent
agent = PitchAnalysisAgent()

# Transcribe a local audio file
result = agent.analyze_pitch("path/to/pitch.mp3")

# Transcribe a local video file
result = agent.analyze_pitch("path/to/pitch.mp4")

# Transcribe from URL
result = agent.analyze_pitch("https://example.com/pitch.mp3")

print(result)
```

## Output Format

The transcription returns a dictionary with:

```json
{
  "success": true,
  "transcription": "Transcribed text...",
  "file_path": "path/to/file.mp3",
  "is_video": false
}
```

For video files, the `is_video` field will be `true`.

## Requirements

- Python 3.8+
- ElevenLabs API key
- Internet connection for API calls
