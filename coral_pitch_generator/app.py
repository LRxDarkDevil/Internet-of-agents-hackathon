import streamlit as st
from dotenv import load_dotenv
import os
import json
from agents.pitch_agent import PitchAgent
from agents.design_agent import DesignAgent
from agents.voice_agent import VoiceAgent
from agents.presentation_agent import PresentationAgent

def main():
    load_dotenv()
    st.title("Startup Pitch Generator")
    st.write("Enter your startup idea/topic below:")
    topic = st.text_input("Startup Idea", "AI in healthcare")
    if st.button("Generate Pitch"):
        # Run agents
        pitch_agent = PitchAgent()
        design_agent = DesignAgent()
        voice_agent = VoiceAgent()
        presentation_agent = PresentationAgent()

        pitch_json = pitch_agent.generate_pitch(topic)
        output_dir = os.path.join("output")
        os.makedirs(output_dir, exist_ok=True)
        pitch_path = os.path.join(output_dir, "pitch.json")
        logo_path = os.path.join(output_dir, "logo.png")
        audio_path = os.path.join(output_dir, "pitch.mp3")
        with open(pitch_path, "w", encoding="utf-8") as f:
            json.dump(pitch_json, f, indent=2)
        design_agent.generate_logo(pitch_json, logo_path)
        voice_agent.narrate_pitch(pitch_json, audio_path)

        st.success("Pitch, logo, and narration generated!")
        st.header("Pitch")
        formatted_pitch = presentation_agent.format_pitch(pitch_json)
        st.markdown(formatted_pitch)
        st.header("Logo")
        st.image(logo_path)
        st.header("Narration")
        audio_file = open(audio_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

if __name__ == "__main__":
    main()
