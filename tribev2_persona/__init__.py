"""
Persona-Based Brain Reaction Predictor
Built on top of Meta's TRIBE v2

Architecture:
    Input (video/audio/text)
        → TRIBE v2 (brain response features)
        → Persona Embedding Layer (user traits)
        → Fusion Network
        → Reaction Prediction
"""

__version__ = "0.1.0"

from .models.pipeline import PersonaReactionPipeline
from .models.persona_encoder import PersonaEncoder, PersonaTraits, PersonaLibrary
from .models.reaction_predictor import (
    ReactionPredictor,
    ReactionPrediction,
    ReactionType,
)
from .models.fusion_module import PersonaFusionModule, BrainRegionMapper
from .models.tribe_wrapper import TribePersonaWrapper

__all__ = [
    "PersonaReactionPipeline",
    "PersonaEncoder",
    "PersonaTraits",
    "PersonaLibrary",
    "ReactionPredictor",
    "ReactionPrediction",
    "ReactionType",
    "PersonaFusionModule",
    "BrainRegionMapper",
    "TribePersonaWrapper",
]
