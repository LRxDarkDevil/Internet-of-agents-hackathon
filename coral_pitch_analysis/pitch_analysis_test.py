"""
Streamlit Test Interface for Pitch Analysis Agent
Test the speech-to-text transcription functionality with audio files.
"""

import streamlit as st
import json
from dotenv import load_dotenv
import os
from agents.pitch_analysis_agent import PitchAnalysisAgent

def main():
    load_dotenv()
    
    st.title("🎯 Pitch Transcription Agent Test")
    st.write("Upload an audio file or provide a URL to transcribe a pitch presentation.")
    
    # Initialize the agent
    try:
        agent = PitchAnalysisAgent()
        st.success("✅ Pitch Transcription Agent initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {e}")
        st.stop()
    
    # Input options
    st.header("📁 Input Options")
    
    input_type = st.radio(
        "Choose input method:",
        ["Upload Audio File", "Audio File URL"]
    )
    
    audio_file = None
    file_path = None
    
    if input_type == "Upload Audio File":
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'ogg'],
            help="Upload an audio file containing a pitch presentation"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with st.spinner("Saving uploaded file..."):
                temp_dir = "temp_uploads"
                os.makedirs(temp_dir, exist_ok=True)
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.success(f"✅ File saved: {uploaded_file.name}")
                audio_file = file_path
    
    else:  # Audio File URL
        url = st.text_input(
            "Enter audio file URL:",
            placeholder="https://example.com/pitch.mp3",
            help="Provide a direct URL to an audio file"
        )
        
        if url:
            audio_file = url
            st.info(f"🌐 Will analyze audio from: {url}")
    
    # Transcription button
    if audio_file:
        st.header("🔍 Transcription")
        
        if st.button("🚀 Transcribe Pitch", type="primary"):
            with st.spinner("🎵 Transcribing pitch..."):
                try:
                    # Perform transcription
                    result = agent.analyze_pitch(audio_file)
                    
                    if result["success"]:
                        st.success("✅ Transcription completed successfully!")
                        
                        # Display results
                        st.header("📊 Transcription Results")
                        
                        # Transcription
                        st.subheader("📝 Transcribed Text")
                        st.text_area(
                            "Transcription:",
                            value=result["transcription"],
                            height=300,
                            disabled=True
                        )
                        
                        # Basic stats
                        word_count = len(result["transcription"].split())
                        st.subheader("📈 Basic Statistics")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Word Count", word_count)
                        with col2:
                            st.metric("Character Count", len(result["transcription"]))
                        
                        # Download results
                        st.subheader("💾 Download Results")
                        results_json = json.dumps(result, indent=2)
                        st.download_button(
                            label="📥 Download Transcription Results (JSON)",
                            data=results_json,
                            file_name="pitch_transcription_results.json",
                            mime="application/json"
                        )
                        
                    else:
                        st.error(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error during transcription: {e}")
                    st.exception(e)
    
    # Cleanup section
    if file_path and os.path.exists(file_path):
        st.header("🧹 Cleanup")
        if st.button("🗑️ Delete Uploaded File"):
            try:
                os.remove(file_path)
                st.success("✅ File deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting file: {e}")
    
    # Instructions
    st.header("📖 Instructions")
    st.markdown("""
    ### How to use this tool:
    
    1. **Upload a file** or **provide a URL** to an audio file containing a pitch presentation
    2. Click **"Transcribe Pitch"** to start the transcription
    3. The tool will:
       - Transcribe the audio to text using ElevenLabs
       - Display the transcribed text
       - Show basic statistics (word count, character count)
       - Allow you to download the results as JSON
    
    ### Supported audio formats:
    - MP3
    - WAV
    - M4A
    - OGG
    """)
    
    # Footer
    st.markdown("---")
    st.caption("🎯 Pitch Transcription Agent - Powered by ElevenLabs Speech-to-Text")

if __name__ == "__main__":
    main()
