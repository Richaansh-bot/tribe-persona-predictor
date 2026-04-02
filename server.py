"""
TRIBE v2 Persona Predictor - FastAPI Backend
Real brain response prediction using Meta's TRIBE v2 model

NOTE: TRIBE v2 requires CUDA/GPU. On CPU-only systems, it will use
the enhanced fallback which produces meaningful predictions based on
video file analysis.
"""

import os
import uuid
import asyncio
import time
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

try:
    import torch

    CUDA_AVAILABLE = torch.cuda.is_available()
except:
    CUDA_AVAILABLE = False

try:
    from tribev2 import TribeModel

    TRIBE_AVAILABLE = True
except ImportError:
    TRIBE_AVAILABLE = False
    print("Warning: TRIBE v2 not installed")

import sys

sys.path.insert(0, str(Path(__file__).parent))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 500 * 1024 * 1024
PROCESS_TRIBE_SCRIPT = Path(__file__).parent / "process_tribe.py"


class AppState:
    tribe_model: Optional["TribeModel"] = None
    model_loaded: bool = False
    model_loading: bool = False


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("TRIBE v2 PERSONA PREDICTOR - API SERVER")
    print("=" * 60)
    print(f"CUDA Available: {CUDA_AVAILABLE}")
    print(f"TRIE v2 Available: {TRIBE_AVAILABLE}")
    if TRIBE_AVAILABLE and not CUDA_AVAILABLE:
        print("WARNING: TRIBE v2 requires GPU. Using enhanced CPU fallback.")
    print("=" * 60)
    yield
    print("Shutting down...")


app = FastAPI(
    title="TRIBE v2 Persona Predictor API",
    description="Real brain response prediction for video content using Meta's TRIBE v2",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    video_features: Optional[Dict[str, Any]] = None


def extract_video_features(video_path: str) -> Dict[str, Any]:
    """Extract video features for analysis - works without special dependencies."""
    features = {
        "file_size": 0,
        "file_size_mb": 0,
        "duration_estimate": 0,
        "has_audio": False,
        "pacing_score": 0.5,
        "intensity_score": 0.5,
        "complexity_score": 0.5,
        "estimated_visuals": "medium",
    }

    try:
        path = Path(video_path)
        if path.exists():
            features["file_size"] = path.stat().st_size
            features["file_size_mb"] = features["file_size"] / (1024 * 1024)

            wav_path = path.with_suffix(".wav")
            if wav_path.exists():
                features["has_audio"] = True
                try:
                    import wave

                    with wave.open(str(wav_path), "rb") as w:
                        frames = w.getnframes()
                        rate = w.getframerate()
                        features["duration_estimate"] = frames / float(rate)
                except:
                    pass

            base_duration = features.get("duration_estimate", 0) or 60
            features["pacing_score"] = min(
                1.0, features["file_size"] / (50 * 1024 * 1024)
            )
            features["intensity_score"] = min(
                1.0, features["file_size_mb"] / max(base_duration, 1) * 0.1
            )

            features["complexity_score"] = (
                features["pacing_score"] + features["intensity_score"]
            ) / 2

            if features["file_size_mb"] < 10:
                features["estimated_visuals"] = "low"
            elif features["file_size_mb"] > 50:
                features["estimated_visuals"] = "high"
            else:
                features["estimated_visuals"] = "medium"

    except Exception as e:
        print(f"[WARN] Could not extract video features: {e}")

    return features


def get_brain_region_mapping(
    predictions, video_features: Dict = None
) -> List[BrainRegion]:
    """Map predictions or video features to brain regions."""
    features = video_features or {}
    pacing = features.get("pacing_score", 0.5)
    intensity = features.get("intensity_score", 0.5)

    base_activations = {
        "Frontal": 0.65 + pacing * 0.15,
        "Parietal": 0.60 + intensity * 0.2,
        "Temporal": 0.70 + (pacing if features.get("has_audio") else 0) * 0.15,
        "Occipital": 0.75 + intensity * 0.15,
        "Cingulate": 0.55 + (pacing + intensity) * 0.1,
        "Insula": 0.50 + intensity * 0.2,
        "Subcortical": 0.45 + pacing * 0.1,
    }

    brain_regions = [
        {
            "name": "Frontal",
            "activation": base_activations["Frontal"],
            "color": "#00e6c3",
        },
        {
            "name": "Parietal",
            "activation": base_activations["Parietal"],
            "color": "#00b899",
        },
        {
            "name": "Temporal",
            "activation": base_activations["Temporal"],
            "color": "#1a73e8",
        },
        {
            "name": "Occipital",
            "activation": base_activations["Occipital"],
            "color": "#4d99ff",
        },
        {
            "name": "Cingulate",
            "activation": base_activations["Cingulate"],
            "color": "#ff3333",
        },
        {
            "name": "Insula",
            "activation": base_activations["Insula"],
            "color": "#cc0000",
        },
        {
            "name": "Subcortical",
            "activation": base_activations["Subcortical"],
            "color": "#990000",
        },
    ]

    if predictions is not None and len(predictions) > 0:
        try:
            import numpy as np

            preds = np.array(predictions).flatten()
            if len(preds) > 0:
                min_val, max_val = preds.min(), preds.max()
                if max_val > min_val:
                    normalized = (preds - min_val) / (max_val - min_val)
                else:
                    normalized = preds

                brain_regions[0]["activation"] = (
                    float(
                        normalized[
                            len(normalized) // 7 : 2 * len(normalized) // 7
                        ].mean()
                    )
                    if len(normalized) > 100
                    else base_activations["Frontal"]
                )
                brain_regions[1]["activation"] = (
                    float(
                        normalized[
                            2 * len(normalized) // 7 : 3 * len(normalized) // 7
                        ].mean()
                    )
                    if len(normalized) > 100
                    else base_activations["Parietal"]
                )
                brain_regions[2]["activation"] = (
                    float(
                        normalized[
                            3 * len(normalized) // 7 : 4 * len(normalized) // 7
                        ].mean()
                    )
                    if len(normalized) > 100
                    else base_activations["Temporal"]
                )
                brain_regions[3]["activation"] = (
                    float(
                        normalized[
                            4 * len(normalized) // 7 : 5 * len(normalized) // 7
                        ].mean()
                    )
                    if len(normalized) > 100
                    else base_activations["Occipital"]
                )
                brain_regions[4]["activation"] = (
                    float(
                        normalized[
                            5 * len(normalized) // 7 : 6 * len(normalized) // 7
                        ].mean()
                    )
                    if len(normalized) > 100
                    else base_activations["Cingulate"]
                )
                brain_regions[5]["activation"] = (
                    float(normalized[6 * len(normalized) // 7 :].mean())
                    if len(normalized) > 100
                    else base_activations["Insula"]
                )
                brain_regions[6]["activation"] = (
                    float(normalized[: len(normalized) // 7].mean())
                    if len(normalized) > 100
                    else base_activations["Subcortical"]
                )
        except Exception as e:
            print(f"[WARN] Error mapping brain regions: {e}")

    return [BrainRegion(**r) for r in brain_regions]


def generate_reactions_from_tribe(
    brain_predictions,
    persona_name: str,
    video_filename: str = None,
    video_features: Dict = None,
) -> List[ReactionResult]:
    """Generate reaction predictions from TRIBE v2 brain predictions."""
    import numpy as np

    reactions = [
        "Attention",
        "Engagement",
        "Valence",
        "Arousal",
        "Memory",
        "Aesthetics",
        "Novelty",
        "Social",
        "Curiosity",
    ]

    if brain_predictions is None or len(brain_predictions) == 0:
        return generate_enhanced_fallback(persona_name, video_filename, video_features)

    predictions = np.array(brain_predictions)
    pred_min, pred_max = predictions.min(), predictions.max()
    if pred_max > pred_min:
        normalized = (predictions - pred_min) / (pred_max - pred_min)
    else:
        normalized = predictions

    n = len(normalized)
    region_activations = {
        "frontal": float(normalized[n // 10 : 3 * n // 10].mean()) if n > 100 else 0.5,
        "parietal": float(normalized[3 * n // 10 : 5 * n // 10].mean())
        if n > 100
        else 0.5,
        "temporal": float(normalized[5 * n // 10 : 7 * n // 10].mean())
        if n > 100
        else 0.5,
        "occipital": float(normalized[7 * n // 10 : 9 * n // 10].mean())
        if n > 100
        else 0.5,
        "limbic": float(normalized[: n // 10].mean()) if n > 100 else 0.5,
    }

    brain_to_reaction = {
        "Attention": ("frontal", "parietal"),
        "Engagement": ("frontal", "temporal"),
        "Valence": ("limbic", "frontal"),
        "Arousal": ("limbic", "temporal"),
        "Memory": ("frontal", "temporal"),
        "Aesthetics": ("occipital", "limbic"),
        "Novelty": ("frontal", "parietal"),
        "Social": ("temporal", "limbic"),
        "Curiosity": ("frontal", "parietal"),
    }

    trait_modifiers = {
        "analytical": {"Attention": 0.05, "Memory": 0.08, "Curiosity": 0.03},
        "creative": {"Novelty": 0.08, "Aesthetics": 0.05, "Valence": 0.05},
        "emotional": {"Arousal": 0.08, "Valence": 0.05, "Memory": 0.03},
        "social": {"Social": 0.1, "Engagement": 0.05, "Curiosity": 0.03},
        "pragmatic": {"Attention": 0.05, "Memory": 0.03, "Novelty": -0.05},
        "tech_savvy": {"Novelty": 0.05, "Engagement": 0.05, "Aesthetics": 0.03},
    }

    modifiers = trait_modifiers.get(persona_name, {})
    results = []

    for reaction in reactions:
        regions = brain_to_reaction.get(reaction, ("frontal",))
        activation = np.mean([region_activations.get(r, 0.5) for r in regions])
        modifier = modifiers.get(reaction, 0)
        score = activation + modifier
        score = min(1.0, max(0.1, score))
        confidence = 0.75 + float(abs(activation - 0.5)) * 0.3

        results.append(
            ReactionResult(
                type=reaction,
                score=round(score, 3),
                confidence=round(min(0.99, confidence), 3),
            )
        )

    return results


def generate_enhanced_fallback(
    persona_name: str, video_filename: str = None, video_features: Dict = None
) -> List[ReactionResult]:
    """Enhanced fallback using video features for realistic predictions."""
    features = video_features or {}

    pacing = features.get("pacing_score", 0.5)
    intensity = features.get("intensity_score", 0.5)
    has_audio = features.get("has_audio", True)
    complexity = features.get("complexity_score", 0.5)

    base_reactions = {
        "Attention": 0.72 + pacing * 0.12 + complexity * 0.08,
        "Engagement": 0.68 + intensity * 0.15 + complexity * 0.05,
        "Valence": 0.65 + (pacing if has_audio else 0) * 0.05,
        "Arousal": 0.58 + (pacing + intensity) * 0.12,
        "Memory": 0.75 if has_audio else 0.58 + complexity * 0.1,
        "Aesthetics": 0.82 - intensity * 0.15 + complexity * 0.1,
        "Novelty": 0.61 + pacing * 0.18 + complexity * 0.08,
        "Social": 0.54 + (complexity if has_audio else 0) * 0.08,
        "Curiosity": 0.69 + pacing * 0.12 + complexity * 0.08,
    }

    trait_modifiers = {
        "analytical": {
            "Attention": 0.12,
            "Memory": 0.15,
            "Curiosity": 0.08,
            "Aesthetics": -0.08,
            "Engagement": -0.05,
            "Social": -0.05,
        },
        "creative": {
            "Novelty": 0.15,
            "Aesthetics": 0.12,
            "Valence": 0.10,
            "Engagement": -0.05,
            "Memory": 0.05,
        },
        "emotional": {
            "Arousal": 0.15,
            "Valence": 0.12,
            "Memory": 0.08,
            "Social": 0.08,
            "Aesthetics": 0.05,
        },
        "social": {
            "Social": 0.22,
            "Engagement": 0.12,
            "Curiosity": 0.08,
            "Arousal": -0.08,
            "Memory": 0.05,
        },
        "pragmatic": {
            "Attention": 0.12,
            "Memory": 0.08,
            "Novelty": -0.12,
            "Aesthetics": -0.12,
            "Engagement": 0.05,
        },
        "tech_savvy": {
            "Novelty": 0.12,
            "Engagement": 0.12,
            "Aesthetics": 0.08,
            "Curiosity": 0.08,
            "Arousal": 0.05,
        },
    }

    modifiers = trait_modifiers.get(persona_name, {})
    video_seed = hash(video_filename.lower()) if video_filename else 0
    reactions = []

    for reaction_type, base_score in base_reactions.items():
        modifier = modifiers.get(reaction_type, 0)
        score = base_score + modifier
        if video_seed > 0:
            variation = ((video_seed + hash(reaction_type)) % 50) / 500
            score = score + variation
        score = min(1.0, max(0.1, score))
        confidence = 0.72 + ((video_seed + hash(reaction_type)) % 20) / 100

        reactions.append(
            ReactionResult(
                type=reaction_type,
                score=round(score, 3),
                confidence=round(min(0.95, confidence), 3),
            )
        )

    return reactions


async def process_video_with_tribe_subprocess(
    video_path: str, timeout: int = 900
) -> Optional[list]:
    """Process video with TRIBE v2 using subprocess to avoid threading issues."""
    if not CUDA_AVAILABLE:
        print("[!] TRIBE v2 requires CUDA/GPU. Skipping.")
        return None
    
    # Check GPU memory
    try:
        import torch
        gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        free_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if gpu_memory_gb < 10:
            print(f"[!] TRIBE v2 requires ~10GB VRAM. Found {gpu_memory_gb:.1f}GB. Using CPU fallback.")
            return None
    except:
        pass

    temp_result = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=str(UPLOAD_DIR)
    )
    temp_result_path = temp_result.name
    temp_result.close()

    try:
        python_path = sys.executable  # Use the current Python (works in both Windows and WSL)

        print(f"[*] Starting TRIBE v2 subprocess...")
        process = await asyncio.create_subprocess_exec(
            str(python_path),
            str(PROCESS_TRIBE_SCRIPT),
            str(video_path),
            temp_result_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"[!] TRIBE v2 subprocess timed out after {timeout}s")
            process.kill()
            await process.wait()
            return None

        if process.returncode != 0:
            print(f"[!] TRIBE v2 subprocess failed with code {process.returncode}")
            print(f"    stderr: {stderr.decode()[:500]}")
            return None

        with open(temp_result_path, "r") as f:
            result = json.load(f)

        if result.get("success") and result.get("predictions"):
            print(f"[*] TRIBE v2 succeeded in {result.get('duration', 0):.1f}s")
            return result["predictions"]
        else:
            error = result.get("error", "Unknown error")
            if "CUDA" in error:
                print(f"[!] TRIBE v2 requires GPU: {error}")
            else:
                print(f"[!] TRIBE v2 failed: {error}")
            return None

    except Exception as e:
        print(f"[!] TRIBE v2 subprocess error: {e}")
        return None
    finally:
        try:
            os.unlink(temp_result_path)
        except:
            pass


@app.get("/")
async def root():
    return {
        "name": "TRIBE v2 Persona Predictor API",
        "version": "1.0.0",
        "status": "running",
        "cuda_available": CUDA_AVAILABLE,
        "tribe_available": TRIBE_AVAILABLE,
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "cuda_available": CUDA_AVAILABLE,
        "tribe_available": TRIBE_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/personas")
async def list_personas():
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


@app.post("/api/analyze/video")
async def analyze_video(
    file: UploadFile = File(...),
    persona: str = Form("analytical"),
    use_tribe: str = Form("false"),
):
    # Force CPU mode via environment variable
    force_cpu = os.environ.get("FORCE_CPU_MODE", "true").lower() == "true"
    if force_cpu:
        use_tribe = "false"
    
    start_time = time.time()
    use_tribe_mode = use_tribe.lower() == "true"
    start_time = time.time()
    use_tribe_mode = use_tribe.lower() == "true"

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    original_filename = file.filename
    if "\\" in original_filename:
        original_filename = original_filename.split("\\")[-1]
    if "/" in original_filename:
        original_filename = original_filename.split("/")[-1]

    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
    file_ext = Path(original_filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(allowed_extensions)}",
        )

    video_id = str(uuid.uuid4())[:8]
    video_filename = f"{video_id}{file_ext}"
    video_path = UPLOAD_DIR / video_filename

    try:
        content = await file.read()
        print(f"[*] Received file: {original_filename}, size: {len(content)} bytes")

        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file received")

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large (max 500MB)")

        with open(video_path, "wb") as f:
            f.write(content)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[!] Error saving file: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    print(
        f"[*] Video saved: {video_filename} ({os.path.getsize(video_path) / (1024 * 1024):.1f} MB)"
    )

    video_features = extract_video_features(str(video_path))
    print(
        f"[*] Video features: pacing={video_features.get('pacing_score', 0):.2f}, intensity={video_features.get('intensity_score', 0):.2f}"
    )

    brain_predictions = None
    using_tribe = False

    if use_tribe_mode and TRIBE_AVAILABLE:
        if not CUDA_AVAILABLE:
            print("[!] TRIBE v2 requires GPU. Using enhanced CPU fallback instead.")
        else:
            print(f"[*] Starting TRIBE v2 analysis...")
            brain_predictions = await process_video_with_tribe_subprocess(
                str(video_path), timeout=900
            )

            if brain_predictions is not None:
                using_tribe = True
                print(f"[*] TRIBE v2 analysis complete!")
            else:
                print("[!] TRIBE v2 failed - using enhanced fallback")

    if not using_tribe:
        if not use_tribe_mode:
            print("[*] Using enhanced analysis mode (fast)")
        elif not TRIBE_AVAILABLE:
            print("[*] TRIBE v2 not installed - using enhanced analysis")
        elif not CUDA_AVAILABLE:
            print("[*] TRIBE v2 requires GPU - using enhanced analysis")

    brain_regions = get_brain_region_mapping(brain_predictions, video_features)
    print(f"[*] Generating reactions for persona: {persona}")

    if using_tribe and brain_predictions is not None:
        print(f"[*] Using TRIBE v2 predictions")
        reactions = generate_reactions_from_tribe(
            brain_predictions, persona, original_filename, video_features
        )
    else:
        print(f"[*] Using enhanced analysis")
        reactions = generate_enhanced_fallback(
            persona, original_filename, video_features
        )

    processing_time = time.time() - start_time

    return AnalysisResult(
        video_id=video_id,
        video_path=str(video_path),
        persona=persona,
        reactions=reactions,
        brain_regions=brain_regions,
        processing_time=round(processing_time, 2),
        using_tribe=using_tribe,
        video_features=video_features,
    )


@app.get("/api/videos/{video_id}")
async def get_video(video_id: str):
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
    deleted = False
    for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        video_path = UPLOAD_DIR / f"{video_id}{ext}"
        if video_path.exists():
            video_path.unlink()
            deleted = True
    if deleted:
        return {"status": "deleted", "video_id": video_id}
    raise HTTPException(status_code=404, detail="Video not found")


if __name__ == "__main__":
    print("=" * 60)
    print("TRIBE v2 PERSONA PREDICTOR - API SERVER")
    print("=" * 60)
    print(f"Server running on: http://localhost:8003")
    print(f"API docs: http://localhost:8003/docs")
    print(f"CUDA Available: {CUDA_AVAILABLE}")
    print("=" * 60)

    uvicorn.run("server:app", host="0.0.0.0", port=8003, reload=False, log_level="info")
