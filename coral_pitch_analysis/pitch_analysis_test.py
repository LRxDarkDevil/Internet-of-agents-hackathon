"""
Streamlit Test Interface for Pitch Analysis Agent
Test the pitch analysis functionality with different input types.
"""

import streamlit as st
import json
from dotenv import load_dotenv
import os
from agents.pitch_analysis_agent import PitchAnalysisAgent

def main():
    load_dotenv()
    
    st.title("🎯 Pitch Analysis Agent")
    st.write("Analyze your pitch with different input types: text, audio, or video.")
    
    # Initialize the agent
    try:
        agent = PitchAnalysisAgent()
        st.success("✅ Pitch Analysis Agent initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize agent: {e}")
        st.stop()
    
    # Pitch Information Form
    st.header("📝 Pitch Information")

    # Initialize session state for pitch type if not exists
    if 'pitch_type' not in st.session_state:
        st.session_state.pitch_type = "text"

    # Radio button for pitch type (outside form for immediate response)
    pitch_type = st.radio("Pitch Type", ["text", "audio", "video"], key="pitch_type_radio")

    with st.form("pitch_form"):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Title", placeholder="Enter your pitch title")
            industry = st.text_input("Industry", placeholder="e.g., Technology, Healthcare, Finance")
            target_market = st.text_input("Target Market", placeholder="e.g., B2B, B2C, Enterprise")
            funding_amount = st.text_input("Funding Amount (Optional)", placeholder="e.g., $100K, $1M")

        with col2:
            description = st.text_area("Description", placeholder="Brief description of your pitch", height=100)
            business_model = st.text_input("Business Model", placeholder="e.g., SaaS, Marketplace, Subscription")

        # File upload section (inside form for immediate display)
        uploaded_file = None
        file_path = None

        if pitch_type == "audio":
            st.header("🎵 Audio File Upload")
            uploaded_file = st.file_uploader(
                "Upload Audio File",
                type=['mp3', 'wav', 'm4a', 'ogg'],
                help="Upload an audio file containing your pitch",
                key="audio_uploader"
            )
        elif pitch_type == "video":
            st.header("🎬 Video File Upload")
            uploaded_file = st.file_uploader(
                "Upload Video File",
                type=['mp4', 'avi', 'mov', 'mkv'],
                help="Upload a video file containing your pitch",
                key="video_uploader"
            )

        # Submit button
        submitted = st.form_submit_button("🚀 Analyze Pitch", type="primary")
    
    # Process the form submission
    if submitted:
        # Validate required fields
        if not title or not description or not industry or not target_market or not business_model:
            st.error("❌ Please fill in all required fields (Title, Description, Industry, Target Market, Business Model)")
        else:
            # Prepare pitch data
            pitch_data = {
                "title": title,
                "description": description,
                "industry": industry,
                "targetMarket": target_market,
                "businessModel": business_model,
                "fundingAmount": funding_amount if funding_amount else "",
                "pitchType": pitch_type,
                "file": None
            }
            
            # Handle file uploads
            if pitch_type in ["audio", "video"] and uploaded_file is not None:
                # Save uploaded file temporarily
                with st.spinner("Saving uploaded file..."):
                    temp_dir = "temp_uploads"
                    os.makedirs(temp_dir, exist_ok=True)
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    st.success(f"✅ File saved: {uploaded_file.name}")
                    pitch_data["file"] = uploaded_file.name
            
            # Process based on pitch type
            if pitch_type == "text":
                st.header("📊 Pitch Analysis Results")
                st.success("✅ Text pitch analysis completed!")
                
                # Display pitch data as JSON
                st.subheader("📝 Pitch Data")
                st.json(pitch_data)
                
                # Download results
                st.subheader("💾 Download Results")
                results_json = json.dumps(pitch_data, indent=2)
                st.download_button(
                    label="📥 Download Pitch Data (JSON)",
                    data=results_json,
                    file_name="pitch_analysis_results.json",
                    mime="application/json"
                )
            
            elif pitch_type == "audio" and uploaded_file is not None:
                st.header("🔍 Audio Pitch Analysis")
                
                with st.spinner("🎵 Transcribing audio..."):
                    try:
                        # Perform transcription
                        transcription_result = agent.analyze_pitch(file_path)
                        
                        if transcription_result["success"]:
                            st.success("✅ Audio transcription completed!")
                            
                            # Add transcription to pitch data
                            pitch_data["pitch"] = transcription_result["transcription"]
                            
                            # Display results
                            st.subheader("📝 Transcribed Text")
                            st.text_area(
                                "Pitch:",
                                value=transcription_result["transcription"],
                                height=200,
                                disabled=True
                            )
                            
                            # Display complete pitch data
                            st.subheader("📊 Complete Pitch Analysis")
                            st.json(pitch_data)
                            
                            # Download results
                            st.subheader("💾 Download Results")
                            results_json = json.dumps(pitch_data, indent=2)
                            st.download_button(
                                label="📥 Download Complete Analysis (JSON)",
                                data=results_json,
                                file_name="pitch_analysis_with_pitch.json",
                                mime="application/json"
                            )
                            
                        else:
                            st.error(f"❌ Transcription failed: {transcription_result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"❌ Error during transcription: {e}")
                        st.exception(e)
            
            elif pitch_type == "video" and uploaded_file is not None:
                st.header("🎬 Video Pitch Analysis")

                with st.spinner("🎥 Extracting audio from video..."):
                    try:
                        # Extract audio from video and perform transcription
                        transcription_result = agent.analyze_pitch(file_path)

                        if transcription_result["success"]:
                            st.success("✅ Video transcription completed!")

                            # Add transcription to pitch data
                            pitch_data["pitch"] = transcription_result["transcription"]

                            # Display results
                            st.subheader("📝 Transcribed Text")
                            st.text_area(
                                "Pitch:",
                                value=transcription_result["transcription"],
                                height=200,
                                disabled=True
                            )

                            # Display complete pitch data
                            st.subheader("📊 Complete Pitch Analysis")
                            st.json(pitch_data)

                            # Download results
                            st.subheader("💾 Download Results")
                            results_json = json.dumps(pitch_data, indent=2)
                            st.download_button(
                                label="📥 Download Complete Analysis (JSON)",
                                data=results_json,
                                file_name="pitch_analysis_with_pitch.json",
                                mime="application/json"
                            )

                        else:
                            st.error(f"❌ Video transcription failed: {transcription_result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"❌ Error during video transcription: {e}")
                        st.exception(e)
            
            elif pitch_type in ["audio", "video"] and uploaded_file is None:
                st.error(f"❌ Please upload a {pitch_type} file for analysis")
    
    # Instructions
    st.header("📖 Instructions")
    st.markdown("""
    1. **Fill in the pitch information** (Title, Description, Industry, Target Market, Business Model)
    2. **Choose pitch type**:
       - **Text**: No file upload needed, just displays the pitch data as JSON
       - **Audio**: Upload an audio file to get transcription + pitch data
       - **Video**: Upload a video file to extract audio, transcribe, and get pitch data
    3. **Click "Analyze Pitch"** to process your pitch
    4. **View results** and download as JSON
    
    ### Supported file formats:
    - **Audio**: MP3, WAV, M4A, OGG
    - **Video**: MP4, AVI, MOV, MKV
    
    ### Output includes:
    - All pitch information fields
    - Pitch content (for audio and video files)
    - File information (if uploaded)
    """)
    
    # Footer
    st.markdown("---")
    st.caption("🎯 Pitch Analysis Agent - Powered by ElevenLabs Speech-to-Text (Audio & Video)")

if __name__ == "__main__":
    main()
