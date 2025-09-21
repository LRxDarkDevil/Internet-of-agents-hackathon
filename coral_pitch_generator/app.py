import streamlit as st
from dotenv import load_dotenv
import os
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from agents.pitch_agent import PitchAgent
from agents.design_agent import DesignAgent
from agents.voice_agent import VoiceAgent
from agents.presentation_agent import PresentationAgent


def save_pitch_as_pdf(text: str) -> BytesIO:
    """Generate a PDF file in memory from the pitch text."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 18
        if y < 50:  # new page if text overflows
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer


def main():
    load_dotenv()
    st.set_page_config(page_title="FoundryAI Startup Pitch Generator", layout="wide")

    # Title Section
    st.markdown(
        """
        <h1 style='text-align:center; color:#7F8C8D;'>🚀 FoundryAI Startup Pitch Generator</h1>
        <p style='text-align:center; font-size:18px; color:#7F8C8D;'>
            FoundryAI Multi-Agent Startup Pitch Generator
            Transform your idea into a professional pitch with logo, narration, and presentation design.
        </p>
        <hr style='margin:20px 0;'>
        """,
        unsafe_allow_html=True
    )

    # Input Section (centered and smaller)
    st.markdown("### 💡 Enter your startup idea/topic below:")

    st.markdown(
        """
        <style>
        .centered-container {
            max-width: 500px;   /* control width */
            margin: 0 auto;     /* center horizontally */
        }
        .stTextInput, .stButton button {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
    topic = st.text_input("", "AI in healthcare", placeholder="e.g., AI-powered financial advisor")
    generate_btn = st.button("✨ Generate Pitch")
    st.markdown("</div>", unsafe_allow_html=True)

    if generate_btn:
        # Run agents
        pitch_agent = PitchAgent()
        design_agent = DesignAgent()
        voice_agent = VoiceAgent()
        presentation_agent = PresentationAgent()

        pitch_json = pitch_agent.generate_pitch(topic)
        output_dir = os.path.join("output")
        os.makedirs(output_dir, exist_ok=True)

        logo_path = os.path.join(output_dir, "logo.png")
        audio_path = os.path.join(output_dir, "pitch.mp3")

        design_agent.generate_logo(pitch_json, logo_path)
        voice_agent.narrate_pitch(pitch_json, audio_path)

        # Save to session_state so screen persists
        st.session_state["pitch_json"] = pitch_json
        st.session_state["logo_path"] = logo_path
        st.session_state["audio_path"] = audio_path

        st.success("✅ Pitch, logo, and narration generated successfully!")

    # Show results if they exist in session_state
    if "pitch_json" in st.session_state:
        pitch_json = st.session_state["pitch_json"]
        logo_path = st.session_state["logo_path"]
        audio_path = st.session_state["audio_path"]

        # Convert pitch JSON to formatted plain text
        presentation_agent = PresentationAgent()
        formatted_pitch = presentation_agent.format_pitch(pitch_json)

        # Presentation Layout
        st.markdown(
            "<h2 style='text-align:center; margin-top:30px;'>📊 Your Startup Presentation</h2>",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1,2,1], gap="large")

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎨 Logo")
            st.image(logo_path, use_container_width=True)
            with open(logo_path, "rb") as f:
                st.download_button("⬇️ Download Logo", f, file_name="logo.png", mime="image/png")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📝 Pitch")
            # Show plain pitch text
            st.text_area("Generated Pitch", formatted_pitch, height=300)

            # Download as TXT
            st.download_button(
                "⬇️ Download Pitch (Text)",
                formatted_pitch,
                file_name="pitch.txt",
                mime="text/plain"
            )

            # Download as PDF
            pdf_file = save_pitch_as_pdf(formatted_pitch)
            st.download_button(
                "⬇️ Download Pitch (PDF)",
                pdf_file,
                file_name="pitch.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎙 Narration")
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button("⬇️ Download Narration", audio_bytes, file_name="pitch.mp3", mime="audio/mpeg")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin-top:40px;'>", unsafe_allow_html=True)

        # Add CSS for cards
        st.markdown(
            """
            <style>
            .card {
                background: #ffffff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
