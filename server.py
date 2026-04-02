"""
TRIBE v2 Persona Predictor - FastAPI Backend
Real brain response prediction using Meta's TRIBE v2 model
"""

import os
import uuid
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import aiofiles

# Thread pool for TRIBE v2 processing
tribe_executor = ThreadPoolExecutor(max_workers=2)

# TRIBE v2 imports
try:
    from tribev2 import TribeModel

    TRIBE_AVAILABLE = True
except ImportError:
    TRIBE_AVAILABLE = False
    print("Warning: TRIBE v2 not installed")

# Persona pipeline imports
import sys

sys.path.insert(0, str(Path(__file__).parent))
from tribev2_persona.models import PersonaLibrary, ReactionType

# ============================================================================
# Configuration
# ============================================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

# ============================================================================
# Global state
# ============================================================================


class AppState:
    tribe_model: Optional["TribeModel"] = None
    model_loaded: bool = False
    model_loading: bool = False


state = AppState()

# ============================================================================
# Lifespan context manager (modern FastAPI approach)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load TRIBE v2 model on startup."""
    print("=" * 60)
    print("LOADING TRIBE v2 MODEL...")
    print("This may take a few minutes on first load...")
    print("=" * 60)

    if TRIBE_AVAILABLE:
        try:
            state.model_loading = True
            state.tribe_model = TribeModel.from_pretrained(
                "facebook/tribev2", cache_folder=str(CACHE_DIR)
            )
            state.model_loaded = True
            print("[OK] TRIBE v2 model loaded successfully!")
            print(f"    Cache folder: {CACHE_DIR}")
        except Exception as e:
            print(f"[!] Failed to load TRIBE v2: {e}")
            print("    Using fallback mode without brain predictions")
    else:
        print("[!] TRIBE v2 not installed")

    state.model_loading = False

    yield  # Server is running

    # Cleanup on shutdown (if needed)
    print("Shutting down TRIBE v2 Persona Predictor API...")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="TRIBE v2 Persona Predictor API",
    description="Real brain response prediction for video content using Meta's TRIBE v2",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Models
# ============================================================================


class PersonaRequest(BaseModel):
    persona: str = "analytical"


class ReactionResult(BaseModel):
    type: str
    score: float
    confidence: float


class BrainRegion(BaseModel):
    name: str
    activation: float
    color: str


class AnalysisResult(BaseModel):
    video_id: str
    video_path: str
    persona: str
    reactions: List[ReactionResult]
    brain_regions: List[BrainRegion]
    processing_time: float
    using_tribe: bool


# ============================================================================
# Helper Functions
# ============================================================================


def get_brain_region_mapping(predictions) -> List[BrainRegion]:
    """Map TRIBE v2 predictions to brain regions."""
    # TRIBE v2 outputs ~20k vertices on fsaverage5 cortical surface
    # We'll aggregate them into major brain regions

    brain_regions = [
        {"name": "Frontal", "activation": 0.0, "color": "#00e6c3"},
        {"name": "Parietal", "activation": 0.0, "color": "#00b899"},
        {"name": "Temporal", "activation": 0.0, "color": "#1a73e8"},
        {"name": "Occipital", "activation": 0.0, "color": "#4d99ff"},
        {"name": "Cingulate", "activation": 0.0, "color": "#ff3333"},
        {"name": "Insula", "activation": 0.0, "color": "#cc0000"},
        {"name": "Subcortical", "activation": 0.0, "color": "#990000"},
    ]

    if predictions is not None and len(predictions) > 0:
        # Normalize predictions to 0-1 range
        preds = predictions.flatten()
        if len(preds) > 0:
            min_val, max_val = preds.min(), preds.max()
            if max_val > min_val:
                normalized = (preds - min_val) / (max_val - min_val)
            else:
                normalized = preds

            # Assign activation based on position (simulated mapping)
            # In real implementation, you'd use proper cortical mapping
            brain_regions[0]["activation"] = (
                float(
                    normalized[len(normalized) // 7 : 2 * len(normalized) // 7].mean()
                )
                if len(normalized) > 100
                else 0.7
            )
            brain_regions[1]["activation"] = (
                float(
                    normalized[
                        2 * len(normalized) // 7 : 3 * len(normalized) // 7
                    ].mean()
                )
                if len(normalized) > 100
                else 0.65
            )
            brain_regions[2]["activation"] = (
                float(
                    normalized[
                        3 * len(normalized) // 7 : 4 * len(normalized) // 7
                    ].mean()
                )
                if len(normalized) > 100
                else 0.72
            )
            brain_regions[3]["activation"] = (
                float(
                    normalized[
                        4 * len(normalized) // 7 : 5 * len(normalized) // 7
                    ].mean()
                )
                if len(normalized) > 100
                else 0.85
            )
            brain_regions[4]["activation"] = (
                float(
                    normalized[
                        5 * len(normalized) // 7 : 6 * len(normalized) // 7
                    ].mean()
                )
                if len(normalized) > 100
                else 0.58
            )
            brain_regions[5]["activation"] = (
                float(normalized[6 * len(normalized) // 7 :].mean())
                if len(normalized) > 100
                else 0.62
            )
            brain_regions[6]["activation"] = (
                float(normalized[: len(normalized) // 7].mean())
                if len(normalized) > 100
                else 0.45
            )

    return [BrainRegion(**r) for r in brain_regions]


def persona_to_reactions(
    persona_name: str, brain_activation: float = 0.7
) -> List[ReactionResult]:
    """Convert persona traits to reaction predictions."""
    persona = PersonaLibrary.get_persona(persona_name)

    # Base reactions influenced by persona traits
    base_reactions = [
        ("Attention", 0.72),
        ("Engagement", 0.68),
        ("Valence", 0.65),
        ("Arousal", 0.58),
        ("Memory", 0.75),
        ("Aesthetics", 0.82),
        ("Novelty", 0.61),
        ("Social", 0.54),
        ("Curiosity", 0.69),
    ]

    # Adjust based on persona traits
    trait_modifiers = {
        "analytical": {"Attention": 0.1, "Memory": 0.15, "Curiosity": 0.05},
        "creative": {"Novelty": 0.15, "Aesthetics": 0.1, "Valence": 0.1},
        "emotional": {"Arousal": 0.15, "Valence": 0.1, "Memory": 0.05},
        "social": {"Social": 0.2, "Engagement": 0.1, "Curiosity": 0.05},
        "pragmatic": {"Attention": 0.1, "Memory": 0.05, "Novelty": -0.1},
        "tech_savvy": {"Novelty": 0.1, "Engagement": 0.1, "Aesthetics": 0.05},
    }

    modifiers = trait_modifiers.get(persona_name, {})
    reactions = []

    for reaction_type, base_score in base_reactions:
        modifier = modifiers.get(reaction_type, 0)
        # Add brain activation influence
        score = min(1.0, max(0.0, base_score * brain_activation + modifier))
        # Add some randomness for demo
        score = min(
            1.0,
            max(0.0, score + (hash(persona_name + reaction_type) % 100) / 500 - 0.1),
        )
        confidence = 0.75 + (hash(persona_name + reaction_type + "conf") % 25) / 100

        reactions.append(
            ReactionResult(
                type=reaction_type,
                score=round(score, 3),
                confidence=round(confidence, 3),
            )
        )

    return reactions


# ============================================================================
# API Endpoints
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "TRIBE v2 Persona Predictor API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "tribe_loaded": state.model_loaded,
        "tribe_loading": state.model_loading,
        "tribe_available": TRIBE_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/personas")
async def list_personas():
    """List available personas."""
    personas = {
        "analytical": {
            "name": "Analytical",
            "icon": "🧠",
            "description": "Logical, detail-oriented, systematic thinker",
            "traits": {
                "openness": 0.7,
                "conscientiousness": 0.8,
                "extraversion": 0.3,
                "emotional": 0.3,
            },
        },
        "creative": {
            "name": "Creative",
            "icon": "✨",
            "description": "Open, imaginative, unconventional approach",
            "traits": {
                "openness": 0.9,
                "conscientiousness": 0.4,
                "extraversion": 0.6,
                "emotional": 0.7,
            },
        },
        "emotional": {
            "name": "Emotional",
            "icon": "💗",
            "description": "High empathy, deeply affected by content",
            "traits": {
                "openness": 0.6,
                "conscientiousness": 0.5,
                "extraversion": 0.5,
                "emotional": 0.9,
            },
        },
        "social": {
            "name": "Social",
            "icon": "👥",
            "description": "Values connections, seeks social validation",
            "traits": {
                "openness": 0.7,
                "conscientiousness": 0.5,
                "extraversion": 0.9,
                "emotional": 0.6,
            },
        },
        "pragmatic": {
            "name": "Pragmatic",
            "icon": "⚡",
            "description": "Practical, results-focused, efficient",
            "traits": {
                "openness": 0.4,
                "conscientiousness": 0.9,
                "extraversion": 0.5,
                "emotional": 0.3,
            },
        },
        "tech_savvy": {
            "name": "Tech Savvy",
            "icon": "🔮",
            "description": "Comfortable with technology, innovative",
            "traits": {
                "openness": 0.8,
                "conscientiousness": 0.7,
                "extraversion": 0.4,
                "emotional": 0.4,
            },
        },
    }
    return {"personas": personas}


# ============================================================================
# Helper Functions for TRIBE v2 Processing
# ============================================================================


def process_video_with_tribe(tribe_model, video_path: str):
    """Process video with TRIBE v2 model in a separate thread."""
    print(f"[*] Extracting features from video...")

    # Get events dataframe from video
    df = tribe_model.get_events_dataframe(video_path=video_path)
    print(f"[*] Events extracted: {len(df)} events")

    print(f"[*] Running brain prediction...")
    # Predict brain responses
    brain_predictions, segments = tribe_model.predict(events=df)
    print(
        f"[*] Predictions shape: {brain_predictions.shape if brain_predictions is not None else 'None'}"
    )

    return brain_predictions


@app.post("/api/analyze/video")
async def analyze_video(
    file: UploadFile = File(...), persona: str = "analytical", use_tribe: str = "false"
):
    """Analyze video and predict brain/persona reactions."""
    start_time = time.time()

    # Parse use_tribe parameter
    use_tribe_mode = use_tribe.lower() == "true"

    if use_tribe_mode:
        print(f"[*] TRIBE v2 mode requested")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(allowed_extensions)}",
        )

    # Generate unique video ID
    video_id = str(uuid.uuid4())[:8]
    video_filename = f"{video_id}{file_ext}"
    video_path = UPLOAD_DIR / video_filename

    # Save uploaded file
    try:
        async with aiofiles.open(video_path, "wb") as f:
            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, detail="File too large (max 500MB)"
                )
            await f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    print(
        f"[*] Video saved: {video_filename} ({os.path.getsize(video_path) / (1024 * 1024):.1f} MB)"
    )

    # Process with TRIBE v2 in background with timeout
    brain_predictions = None
    using_tribe = False

    if use_tribe_mode:
        # Use TRIBE v2 mode (slow but more accurate)
        if state.model_loaded and state.tribe_model is not None:
            try:
                print(f"[*] Starting TRIBE v2 analysis...")
                loop = asyncio.get_event_loop()
                brain_predictions = await asyncio.wait_for(
                    loop.run_in_executor(
                        tribe_executor,
                        lambda: process_video_with_tribe(
                            state.tribe_model, str(video_path)
                        ),
                    ),
                    timeout=600.0,  # 10 minute timeout
                )
                using_tribe = True
                print(f"[*] TRIBE v2 analysis complete!")
            except asyncio.TimeoutError:
                print(
                    "[!] TRIBE v2 processing timed out - falling back to persona mode"
                )
                using_tribe = False
            except Exception as e:
                print(f"[!] TRIBE v2 failed: {e} - falling back to persona mode")
                using_tribe = False
        else:
            print("[!] TRIBE v2 not loaded - falling back to persona mode")
    else:
        # Use fast fallback mode
        print("[*] Using fast fallback mode (persona-based predictions)")

    # Calculate brain activation level from predictions
    brain_activation = 0.7
    if brain_predictions is not None:
        try:
            brain_activation = (
                float(brain_predictions.mean()) if len(brain_predictions) > 0 else 0.7
            )
            # Normalize to 0-1 range
            brain_activation = max(0.3, min(0.95, brain_activation + 0.5))
        except:
            brain_activation = 0.7

    # Generate reactions based on persona
    print(f"[*] Generating reactions for persona: {persona}")
    reactions = persona_to_reactions(persona, brain_activation)

    # Map to brain regions
    brain_regions = get_brain_region_mapping(brain_predictions)

    # Calculate processing time
    processing_time = time.time() - start_time

    return AnalysisResult(
        video_id=video_id,
        video_path=str(video_path),
        persona=persona,
        reactions=reactions,
        brain_regions=brain_regions,
        processing_time=round(processing_time, 2),
        using_tribe=using_tribe,
    )


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
    """Get video file by ID."""
    for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        video_path = UPLOAD_DIR / f"{video_id}{ext}"
        if video_path.exists():
            return FileResponse(
                str(video_path),
                media_type=f"video/{ext[1:]}",
                filename=f"{video_id}{ext}",
            )
    raise HTTPException(status_code=404, detail="Video not found")


@app.delete("/api/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete video file by ID."""
    deleted = False
    for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        video_path = UPLOAD_DIR / f"{video_id}{ext}"
        if video_path.exists():
            video_path.unlink()
            deleted = True
    if deleted:
        return {"status": "deleted", "video_id": video_id}
    raise HTTPException(status_code=404, detail="Video not found")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TRIBE v2 PERSONA PREDICTOR - API SERVER")
    print("=" * 60)
    print(f"Server running on: http://localhost:8003")
    print(f"API docs: http://localhost:8003/docs")
    print("=" * 60)

    uvicorn.run("server:app", host="0.0.0.0", port=8003, reload=False, log_level="info")
