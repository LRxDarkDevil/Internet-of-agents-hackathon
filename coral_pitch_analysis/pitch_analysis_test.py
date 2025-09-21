"""
Streamlit Test Interface for Pitch Analysis Agent
Test the pitch analysis functionality with different input types.
"""

import streamlit as st
import json
from dotenv import load_dotenv
import os
from typing import Dict, Any, Optional
from agents.pitch_analysis_agent import PitchAnalysisAgent

def _display_analysis_results(analysis: Dict[str, Any]):
    """Display comprehensive analysis results in a user-friendly format."""
    st.header("📊 Comprehensive Pitch Analysis")
    st.info("🤖 **Powered by Mistral AI** - Advanced pitch evaluation and market intelligence")

    # Analysis ID and basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Analysis ID", analysis.get("id", "N/A")[:8] + "...")
    with col2:
        st.metric("Overall Score", f"{analysis.get('overallScore', 0)}/100")
    with col3:
        st.metric("NFT Eligible", "✅ Yes" if analysis.get("nftEligible", False) else "❌ No")

    # Category Scores
    st.subheader("📈 Category Scores")
    scores = analysis.get("categoryScores", {})
    cols = st.columns(len(scores))
    score_items = list(scores.items())

    for i, (category, score) in enumerate(score_items):
        with cols[i]:
            st.metric(category.replace("_", " ").title(), f"{score}/100")

    # Response
    response = analysis.get("response", "")
    if response:
        st.subheader("💬 AI Response & Feedback")
        st.write(f"*{response}*")

    # Keynotes (for audio/video)
    keynotes = analysis.get("keynotes", [])
    if keynotes:
        st.subheader("🎯 Key Points")
        for i, keynote in enumerate(keynotes, 1):
            st.write(f"**{i}.** {keynote}")

    # Feedback sections
    feedback = analysis.get("feedback", {})

    # Strengths
    if feedback.get("strengths"):
        st.subheader("✅ Strengths")
        for strength in feedback["strengths"]:
            st.success(f"• {strength}")

    # Improvements
    if feedback.get("improvements"):
        st.subheader("🔧 Areas for Improvement")
        for improvement in feedback["improvements"]:
            st.warning(f"• {improvement}")

    # Recommendations
    if feedback.get("recommendations"):
        st.subheader("💡 Recommendations")
        for recommendation in feedback["recommendations"]:
            st.info(f"• {recommendation}")

    # Market Analysis
    market_analysis = analysis.get("marketAnalysis", {})
    if market_analysis:
        st.subheader("📊 Market Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Market Size:**", market_analysis.get("size", "TBD"))
            st.write("**Growth Rate:**", market_analysis.get("growth", "TBD"))

        with col2:
            st.write("**Competition:**", market_analysis.get("competition", "TBD"))

        # Market trends
        trends = market_analysis.get("trends", [])
        if trends:
            st.write("**Key Trends:**")
            for trend in trends:
                st.write(f"• {trend}")

    # Voice Analysis (if available)
    voice_analysis = analysis.get("voiceAnalysis")
    if voice_analysis:
        st.subheader("🎤 Voice Analysis")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Clarity", f"{voice_analysis.get('clarity', 0)}/100")
        with col2:
            st.metric("Pace", f"{voice_analysis.get('pace', 0)}/100")
        with col3:
            st.metric("Confidence", f"{voice_analysis.get('confidence', 0)}/100")

        # Voice suggestions
        suggestions = voice_analysis.get("suggestions", [])
        if suggestions:
            st.write("**Suggestions:**")
            for suggestion in suggestions:
                st.write(f"• {suggestion}")

    # Agents Used
    agents_used = analysis.get("agentsUsed", [])
    if agents_used:
        st.subheader("🤖 Agents Used")
        st.write(", ".join(agents_used))

    # Download section
    st.subheader("💾 Download Results")
    analysis_json = json.dumps(analysis, indent=2)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Complete Analysis (JSON)",
            data=analysis_json,
            file_name=f"pitch_analysis_{analysis.get('id', 'unknown')}.json",
            mime="application/json"
        )

    with col2:
        # Create summary text for download
        summary_text = f"""
PITCH ANALYSIS REPORT
====================

Analysis ID: {analysis.get("id", "N/A")}
Overall Score: {analysis.get("overallScore", 0)}/100
NFT Eligible: {"Yes" if analysis.get("nftEligible", False) else "No"}

AI RESPONSE & FEEDBACK:
{analysis.get("response", "No response available")}

CATEGORY SCORES:
- Market Opportunity: {scores.get("marketOpportunity", 0)}/100
- Business Model: {scores.get("businessModel", 0)}/100
- Presentation: {scores.get("presentation", 0)}/100
- Financial Viability: {scores.get("financialViability", 0)}/100
- Innovation: {scores.get("innovation", 0)}/100

"""

        # Add keynotes if available
        keynotes = analysis.get("keynotes", [])
        if keynotes:
            summary_text += f"""
KEY POINTS:
{chr(10).join(f"- {keynote}" for keynote in keynotes)}

"""

        summary_text += f"""
Generated by: {", ".join(agents_used)}
Timestamp: {analysis.get("createdAt", "N/A")}
"""
        st.download_button(
            label="📄 Download Summary (Text)",
            data=summary_text,
            file_name=f"pitch_analysis_summary_{analysis.get('id', 'unknown')}.txt",
            mime="text/plain"
        )

def main():
    load_dotenv()

    st.title("🎯 Pitch Analysis Agent")
    st.write("Analyze your pitch with different input types using **Mistral AI** for comprehensive evaluation.")

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

                # Generate comprehensive analysis
                with st.spinner("🤖 Generating comprehensive analysis..."):
                    analysis_result = agent.generate_comprehensive_analysis(pitch_data)

                if analysis_result["success"]:
                    analysis = analysis_result["analysis"]

                    # Display comprehensive analysis
                    _display_analysis_results(analysis)
                else:
                    st.error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                    # Fallback to basic display
                    st.subheader("📝 Pitch Data")
                    st.json(pitch_data)
            
            elif pitch_type == "audio" and uploaded_file is not None:
                st.header("🔍 Audio Pitch Analysis")
                
                with st.spinner("🎵 Transcribing audio..."):
                    try:
                        # Perform transcription
                        transcription_result = agent.analyze_pitch(file_path)
                        
                        if transcription_result["success"]:
                            st.success("✅ Audio transcription completed!")
                            
                            # Add transcription to pitch data
                            transcription_text = transcription_result["transcription"]
                            pitch_data["pitch"] = transcription_text

                            # Check if this is a fallback transcription due to API limits
                            if "[TRANSCRIPTION UNAVAILABLE" in transcription_text:
                                st.warning("⚠️ **Limited Transcription**: Audio transcription is currently unavailable due to API limits. Using fallback mode.")
                                st.info("💡 **Next Steps**: \n- You can still proceed with analysis using the pitch information you've provided\n- The AI will analyze based on your pitch details and description\n- Consider trying again later when API limits are resolved")
                            
                            # Generate comprehensive analysis
                            with st.spinner("🤖 Generating comprehensive analysis..."):
                                analysis_result = agent.generate_comprehensive_analysis(pitch_data)

                            if analysis_result["success"]:
                                analysis = analysis_result["analysis"]

                                # Display transcribed text
                                st.subheader("📝 Transcribed Text")
                                st.text_area(
                                    "Pitch:",
                                    value=transcription_result["transcription"],
                                    height=200,
                                    disabled=True
                                )

                                # Display comprehensive analysis
                                _display_analysis_results(analysis)
                            else:
                                st.error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                            
                        else:
                            error_msg = transcription_result.get('error', 'Unknown error')
                            st.error(f"❌ Transcription failed: {error_msg}")
                            if '429' in str(error_msg) or 'system_busy' in str(error_msg) or 'heavy traffic' in str(error_msg):
                                st.warning("⚠️ **API Rate Limit**: The transcription service is currently experiencing heavy traffic. Please try again in a few minutes.")
                                st.info("💡 **Suggestions**: \n- Wait 2-3 minutes before retrying\n- Try uploading a shorter audio file\n- Consider using the text input option instead")
                            
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
                            transcription_text = transcription_result["transcription"]
                            pitch_data["pitch"] = transcription_text

                            # Check if this is a fallback transcription due to API limits
                            if "[TRANSCRIPTION UNAVAILABLE" in transcription_text:
                                st.warning("⚠️ **Limited Transcription**: Video transcription is currently unavailable due to API limits. Using fallback mode.")
                                st.info("💡 **Next Steps**: \n- You can still proceed with analysis using the pitch information you've provided\n- The AI will analyze based on your pitch details and description\n- Consider trying again later when API limits are resolved")

                            # Generate comprehensive analysis
                            with st.spinner("🤖 Generating comprehensive analysis..."):
                                analysis_result = agent.generate_comprehensive_analysis(pitch_data)

                            if analysis_result["success"]:
                                analysis = analysis_result["analysis"]

                                # Display transcribed text
                                st.subheader("📝 Transcribed Text")
                                st.text_area(
                                    "Pitch:",
                                    value=transcription_result["transcription"],
                                    height=200,
                                    disabled=True
                                )

                                # Display comprehensive analysis
                                _display_analysis_results(analysis)
                            else:
                                st.error(f"❌ Analysis failed: {analysis_result.get('error', 'Unknown error')}")

                        else:
                            error_msg = transcription_result.get('error', 'Unknown error')
                            st.error(f"❌ Video transcription failed: {error_msg}")
                            if '429' in str(error_msg) or 'system_busy' in str(error_msg) or 'heavy traffic' in str(error_msg):
                                st.warning("⚠️ **API Rate Limit**: The transcription service is currently experiencing heavy traffic. Please try again in a few minutes.")
                                st.info("💡 **Suggestions**: \n- Wait 2-3 minutes before retrying\n- Try uploading a shorter video file\n- Consider using the text input option instead")

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
       - **Text**: Enter pitch content directly for **Mistral AI** analysis
       - **Audio**: Upload an audio file for transcription + **Mistral AI** analysis
       - **Video**: Upload a video file for audio extraction, transcription + **Mistral AI** analysis
    3. **Click "Analyze Pitch"** to process your pitch with **Mistral AI**
    4. **View comprehensive results** generated by **Mistral AI** including scores, feedback, and market analysis
    5. **Download results** as JSON or summary text

    ### Supported file formats:
    - **Audio**: MP3, WAV, M4A, OGG
    - **Video**: MP4, AVI, MOV, MKV

    ### 🔄 API Rate Limits:
    - The system includes automatic retry logic for temporary API issues
    - If you encounter rate limits, the system will automatically retry with exponential backoff
    - Consider using text input mode if audio/video transcription consistently fails

    ### 🤖 Mistral AI Analysis includes:
    - **AI Response & Feedback** - Comprehensive response with actionable feedback, key points to highlight, improvements, and ideas
    - **Key Points** - Main highlights from audio/video pitches
    - **Overall Score** (70-100 rating) generated by Mistral AI
    - **Category Scores** (Market Opportunity, Business Model, Presentation, Financial Viability, Innovation) by Mistral AI
    - **Detailed Feedback** (Strengths, Improvements, Recommendations) from Mistral AI
    - **Market Analysis** (Size, Growth, Competition, Trends) analyzed by Mistral AI
    - **Voice Analysis** (Clarity, Pace, Confidence - for audio/video) evaluated by Mistral AI
    - **NFT Eligibility** status determined by Mistral AI
    """)
    
    # Footer
    st.markdown("---")
    st.caption("🎯 Pitch Analysis Agent - Powered by **Mistral AI** for comprehensive analysis | ElevenLabs for speech-to-text")


if __name__ == "__main__":
    main()
