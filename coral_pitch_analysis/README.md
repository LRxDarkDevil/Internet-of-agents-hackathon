# Coral Pitch Analysis

A speech-to-text tool that transcribes audio pitch presentations using ElevenLabs.

## Features

- 🎵 **Audio Transcription**: Convert audio files (MP3, WAV, M4A, OGG) to text using ElevenLabs
- 🌐 **URL Support**: Transcribe audio files from URLs or local uploads
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

### Using the Agent Directly

```python
from agents.pitch_analysis_agent import PitchAnalysisAgent

# Initialize agent
agent = PitchAnalysisAgent()

# Transcribe a local file
result = agent.analyze_pitch("path/to/pitch.mp3")

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
  "file_path": "path/to/file.mp3"
}
```

## Requirements

- Python 3.8+
- ElevenLabs API key
- Internet connection for API calls
