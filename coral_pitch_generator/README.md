# Coral Protocol Multi-Agent Startup Pitch Generator

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your API keys to `.env`:
   ```
   MISTRAL_API_KEY=your_key_here
   AI_ML_API_KEY=your_key_here
   ELEVENLABS_API_KEY=your_key_here
   ```
3. Run:
   ```bash
   python main.py "Fintech for Small Businesses"
   ```

## Output
- `output/pitch.json`: Structured pitch
- `output/logo.png`: Generated logo/slide
- `output/pitch.mp3`: Narration audio

## Stretch Goals
- Register agents in Coral Registry
- Add more pitch sections
- Multiple voices/styles in ElevenLabs
