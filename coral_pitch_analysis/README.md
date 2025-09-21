# Coral Pitch Analysis

A comprehensive pitch analysis tool that uses **Mistral AI** for intelligent evaluation and ElevenLabs for speech-to-text transcription.

## Features

- 🤖 **Mistral AI Analysis**: Comprehensive pitch evaluation using advanced AI
- 🎵 **Audio Transcription**: Convert audio files (MP3, WAV, M4A, OGG) to text using ElevenLabs
- 🎬 **Video Transcription**: Extract audio from video files (MP4, AVI, MOV, MKV) and transcribe using ElevenLabs
- 📊 **Detailed Scoring**: 70-100 rating scale with category breakdowns
- 💬 **AI Feedback**: Strengths, improvements, and recommendations from Mistral AI
- 📈 **Market Analysis**: Size, growth, competition, and trends analysis
- 🎤 **Voice Analysis**: Clarity, pace, and confidence evaluation for presentations
- 🏆 **NFT Eligibility**: Automated qualification assessment
-  **URL Support**: Transcribe audio/video files from URLs or local uploads
- 📱 **Streamlit Interface**: Beautiful web interface for comprehensive analysis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
MISTRAL_API_KEY=your_mistral_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

3. Run the Streamlit test interface:
```bash
streamlit run pitch_analysis_test.py
```

## Usage

### Using the Streamlit Interface

1. Open the web interface
2. Fill in pitch information (Title, Description, Industry, etc.)
3. Choose pitch type (Text, Audio, or Video)
4. Upload files if needed
5. Click "Analyze Pitch" for **Mistral AI** comprehensive analysis
6. View detailed results including scores, feedback, and market analysis
7. Download results as JSON or summary text

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

The comprehensive analysis returns a detailed dictionary with:

```json
{
  "id": "uuid-analysis-id",
  "overallScore": 85,
  "categoryScores": {
    "marketOpportunity": 85,
    "businessModel": 80,
    "presentation": 85,
    "financialViability": 80,
    "innovation": 85
  },
  "feedback": {
    "strengths": ["Clear value proposition", "Strong market understanding"],
    "improvements": ["More detailed financials needed"],
    "recommendations": ["Add customer testimonials"]
  },
  "marketAnalysis": {
    "size": "$2.5B",
    "growth": "15% annually",
    "competition": "Moderate",
    "trends": ["Digital transformation", "Market growth"]
  },
  "voiceAnalysis": {
    "clarity": 85,
    "pace": 80,
    "confidence": 85
  },
  "nftEligible": true,
  "createdAt": "2025-01-21T10:30:00.000Z",
  "agentsUsed": ["Pitch Analysis Agent", "Mistral Analysis Agent"]
}
```

## Requirements

- Python 3.8+
- **Mistral AI API key** (required for comprehensive analysis)
- ElevenLabs API key (for speech-to-text transcription)
- Internet connection for API calls
