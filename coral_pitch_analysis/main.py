"""
FastAPI application for Coral Pitch Analysis
Exposes pitch analysis functionality as REST API endpoints
"""

import os
import tempfile
import shutil
from typing import Optional, Dict, Any, Union
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import the existing agents
try:
    from agents.pitch_analysis_agent import PitchAnalysisAgent
    from agents.mistral_analysis_agent import MistralAnalysisAgent
except ImportError:
    # Handle relative imports when running as main
    from .agents.pitch_analysis_agent import PitchAnalysisAgent
    from .agents.mistral_analysis_agent import MistralAnalysisAgent

# Initialize FastAPI app
app = FastAPI(
    title="Coral Pitch Analysis API",
    description="API for analyzing startup pitch presentations using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests and responses
class PitchAnalysisRequest(BaseModel):
    """Request model for pitch analysis"""
    title: str = Field(..., description="Pitch title")
    description: str = Field(..., description="Pitch description")
    industry: str = Field(..., description="Industry sector")
    targetMarket: str = Field(..., description="Target market")
    businessModel: str = Field(..., description="Business model")
    fundingAmount: str = Field(..., description="Funding amount requested")
    pitchType: str = Field(..., description="Type of pitch: text, audio, or video")
    pitch: str = Field(..., description="Pitch content text")
    languageCode: str = Field(default="eng", description="Language code for transcription")

class PitchAnalysisResponse(BaseModel):
    """Response model for pitch analysis"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    transcription: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str

# Global agent instances
pitch_agent = None
mistral_agent = None

def initialize_agents():
    """Initialize the analysis agents"""
    global pitch_agent, mistral_agent

    try:
        pitch_agent = PitchAnalysisAgent()
        mistral_agent = MistralAnalysisAgent()
        print("SUCCESS: All agents initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize agents: {e}")
        raise

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    """Initialize agents when the application starts"""
    initialize_agents()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Coral Pitch Analysis API is running",
        version="1.0.0"
    )

@app.post("/analyze/text", response_model=PitchAnalysisResponse)
async def analyze_text_pitch(request: PitchAnalysisRequest):
    """
    Analyze a pitch from text input

    Args:
        request: PitchAnalysisRequest containing pitch details and content

    Returns:
        PitchAnalysisResponse with comprehensive analysis
    """
    try:
        if not pitch_agent or not mistral_agent:
            initialize_agents()

        # Prepare pitch data
        pitch_data = {
            "id": f"pitch_{int(__import__('time').time())}",
            "title": request.title,
            "description": request.description,
            "industry": request.industry,
            "targetMarket": request.targetMarket,
            "businessModel": request.businessModel,
            "fundingAmount": request.fundingAmount,
            "pitchType": request.pitchType,
            "pitch": request.pitch,
            "languageCode": request.languageCode
        }

        # Generate comprehensive analysis
        result = pitch_agent.generate_comprehensive_analysis(pitch_data)

        if result["success"]:
            return PitchAnalysisResponse(
                success=True,
                analysis=result["analysis"]
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        print(f"Error in text analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/file", response_model=PitchAnalysisResponse)
async def analyze_file_pitch(
    title: str = Form(..., description="Pitch title"),
    description: str = Form(..., description="Pitch description"),
    industry: str = Form(..., description="Industry sector"),
    targetMarket: str = Form(..., description="Target market"),
    businessModel: str = Form(..., description="Business model"),
    fundingAmount: str = Form(..., description="Funding amount requested"),
    languageCode: str = Form(default="eng", description="Language code for transcription"),
    file: UploadFile = File(..., description="Audio or video file for analysis")
):
    """
    Analyze a pitch from uploaded audio/video file

    Args:
        title: Pitch title
        description: Pitch description
        industry: Industry sector
        targetMarket: Target market
        businessModel: Business model
        fundingAmount: Funding amount requested
        languageCode: Language code for transcription
        file: Uploaded audio or video file

    Returns:
        PitchAnalysisResponse with transcription and comprehensive analysis
    """
    try:
        if not pitch_agent or not mistral_agent:
            initialize_agents()

        # Validate file type
        allowed_extensions = ['.mp3', '.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.wav']
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Read file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Analyze the pitch file
            analysis_result = pitch_agent.analyze_pitch(temp_file_path, languageCode)

            if not analysis_result["success"]:
                raise HTTPException(
                    status_code=500,
                    detail=f"File analysis failed: {analysis_result.get('error', 'Unknown error')}"
                )

            # Prepare pitch data for comprehensive analysis
            pitch_data = {
                "id": f"pitch_{int(__import__('time').time())}",
                "title": title,
                "description": description,
                "industry": industry,
                "targetMarket": targetMarket,
                "businessModel": businessModel,
                "fundingAmount": fundingAmount,
                "pitchType": "audio" if file_extension in ['.mp3', '.wav'] else "video",
                "pitch": analysis_result["transcription"],
                "file": temp_file_path,
                "languageCode": languageCode
            }

            # Generate comprehensive analysis
            comprehensive_result = pitch_agent.generate_comprehensive_analysis(pitch_data)

            if comprehensive_result["success"]:
                return PitchAnalysisResponse(
                    success=True,
                    analysis=comprehensive_result["analysis"],
                    transcription=analysis_result["transcription"]
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Comprehensive analysis failed: {comprehensive_result.get('error', 'Unknown error')}"
                )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in file analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/transcribe")
async def transcribe_audio_url(url: str, language_code: str = "eng"):
    """
    Transcribe audio from a URL

    Args:
        url: URL to audio file
        language_code: Language code for transcription

    Returns:
        Dict with transcription result
    """
    try:
        if not pitch_agent:
            initialize_agents()

        transcription = pitch_agent.transcribe_audio_file(url, language_code)

        if transcription:
            return {
                "success": True,
                "transcription": transcription,
                "url": url
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to transcribe audio from URL"
            )

    except Exception as e:
        print(f"Error in URL transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Coral Pitch Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "text_analysis": "/analyze/text",
            "file_analysis": "/analyze/file",
            "url_transcription": "/analyze/transcribe",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )