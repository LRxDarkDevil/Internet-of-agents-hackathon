# Load environment variables early
from dotenv import load_dotenv
load_dotenv()
import os
import sys
import json
# from coral_sdk import CoralSession  # Coral Protocol integration placeholder
from agents.pitch_agent import PitchAgent
from agents.design_agent import DesignAgent
from agents.voice_agent import VoiceAgent

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<topic/domain>\"")
        sys.exit(1)
    topic = sys.argv[1]

    load_dotenv()
    # session = CoralSession()  # Coral Protocol integration placeholder

    pitch_agent = PitchAgent()
    design_agent = DesignAgent()
    voice_agent = VoiceAgent()

    # Step 1: Generate pitch
    pitch_json = pitch_agent.generate_pitch(topic)
    with open(os.path.join(OUTPUT_DIR, 'pitch.json'), 'w') as f:
        json.dump(pitch_json, f, indent=2)

    # Step 2: Generate logo/slide
    logo_path = os.path.join(OUTPUT_DIR, 'logo.png')
    design_agent.generate_logo(pitch_json, logo_path)

    # Step 3: Generate narration
    audio_path = os.path.join(OUTPUT_DIR, 'pitch.mp3')
    voice_agent.narrate_pitch(pitch_json, audio_path)

    print(f"Pitch, logo, and narration saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
