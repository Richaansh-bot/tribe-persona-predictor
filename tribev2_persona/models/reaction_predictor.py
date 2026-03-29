"""
Reaction Prediction Head - Maps brain responses to interpretable reactions.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np


class ReactionType(Enum):
    """Types of reactions we can predict."""

    ATTENTION = "attention"  # Level of attention/focus
    ENGAGEMENT = "engagement"  # Overall engagement level
    EMOTION_VALENCE = "emotion_valence"  # Positive vs negative response
    EMOTION_AROUSAL = "emotion_arousal"  # Intensity of emotional response
    MEMORY_ENCODING = "memory_encoding"  # How well something will be remembered
    AESTHETIC_APPEAL = "aesthetic_appeal"  # Beauty/artistic appreciation
    NOVELTY_RESPONSE = "novelty_response"  # Response to new/unexpected stimuli
    SOCIAL_CUE_RESPONSE = "social_cue"  # Response to social information
    NARRATIVE_CURIOSITY = "curiosity"  # Interest in continuing


@dataclass
class ReactionPrediction:
    """Container for reaction prediction results."""

    reaction_type: ReactionType
    score: float  # 0-1 scale
    confidence: float  # Model confidence
    brain_region_activation: Optional[Dict[str, float]] = None

    def describe(self) -> str:
        """Human-readable description."""
        type_descriptions = {
            ReactionType.ATTENTION: f"Attention: {self.score:.2f}",
            ReactionType.ENGAGEMENT: f"Engagement: {self.score:.2f}",
            ReactionType.EMOTION_VALENCE: f"Valence: {'Positive' if self.score > 0.5 else 'Negative'} ({self.score:.2f})",
            ReactionType.EMOTION_AROUSAL: f"Arousal: {self.score:.2f}",
            ReactionType.MEMORY_ENCODING: f"Memory: {self.score:.2f}",
            ReactionType.AESTHETIC_APPEAL: f"Aesthetics: {self.score:.2f}",
            ReactionType.NOVELTY_RESPONSE: f"Novelty: {self.score:.2f}",
            ReactionType.SOCIAL_CUE_RESPONSE: f"Social: {self.score:.2f}",
            ReactionType.NARRATIVE_CURIOSITY: f"Curiosity: {self.score:.2f}",
        }
        return type_descriptions.get(self.reaction_type, f"Unknown: {self.score:.2f}")


class ReactionPredictor(nn.Module):
    """
    Neural network that predicts various reaction types from brain features.

    Takes the persona-conditioned brain response and outputs predictions
    for multiple reaction types.
    """

    def __init__(
        self,
        brain_dim: int = 20480,  # fsaverage5 vertices
        hidden_dim: int = 512,
        num_reaction_types: int = 9,
        dropout: float = 0.2,
    ):
        super().__init__()

        self.brain_dim = brain_dim
        self.hidden_dim = hidden_dim
        self.num_reaction_types = num_reaction_types

        # Brain region projectors (project from full brain to hidden)
        self.brain_projector = nn.Sequential(
            nn.Linear(brain_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim * 2, hidden_dim),
        )

        # Temporal pooling (if brain response has time dimension)
        self.temporal_pool = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=8, dropout=dropout
        )

        # Shared encoding for brain patterns
        self.brain_encoder = nn.Sequential(
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
        )

        # Per-reaction-type prediction heads
        self.reaction_heads = nn.ModuleDict()

        for reaction in ReactionType:
            self.reaction_heads[reaction.value] = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim // 2, 1),
                nn.Sigmoid(),  # Output 0-1
            )

        # Confidence estimator
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, num_reaction_types),
            nn.Sigmoid(),
        )

        # Brain region importance for each reaction type
        # Maps cortical regions to reaction relevance
        self._init_region_importance()

    def _init_region_importance(self):
        """Initialize brain region importance weights."""
        self.region_importance = nn.Parameter(
            torch.randn(self.num_reaction_types, 7)  # 7 major cortical regions
        )

    def _pool_brain_response(self, brain_response: torch.Tensor) -> torch.Tensor:
        """
        Pool brain response across vertices and optionally time.

        Args:
            brain_response: Shape (batch, vertices) or (batch, time, vertices)
        """
        if brain_response.dim() == 2:
            # Already pooled across time
            return brain_response

        elif brain_response.dim() == 3:
            # Temporal dimension - pool across time
            batch, time, vertices = brain_response.shape

            # Project first
            pooled = self.brain_projector(brain_response)  # (batch, time, hidden)

            # Attention-based temporal pooling
            pooled = pooled.transpose(0, 1)  # (time, batch, hidden)
            attended, _ = self.temporal_pool(pooled, pooled, pooled)
            attended = attended.transpose(0, 1)  # (batch, time, hidden)

            # Take mean across time
            return attended.mean(dim=1)  # (batch, hidden)

        else:
            raise ValueError(f"Unexpected brain_response shape: {brain_response.shape}")

    def _estimate_confidence(
        self, brain_features: torch.Tensor, predictions: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """Estimate confidence for each prediction based on brain features."""
        confidence = self.confidence_head(brain_features)
        return {rt.value: confidence[:, i : i + 1] for i, rt in enumerate(ReactionType)}

    def forward(
        self, brain_response: torch.Tensor, return_confidence: bool = True
    ) -> Tuple[Dict[str, torch.Tensor], Dict[str, torch.Tensor]]:
        """
        Predict reactions from brain response.

        Args:
            brain_response: Shape (batch, ...) - TRIBE v2 brain predictions
            return_confidence: Whether to estimate prediction confidence

        Returns:
            predictions: Dict mapping ReactionType -> scores (0-1)
            confidence: Dict mapping ReactionType -> confidence scores
        """
        # Pool brain response
        features = self._pool_brain_response(brain_response)  # (batch, hidden)

        # Encode brain patterns
        encoded = self.brain_encoder(features) + features  # Residual

        # Predict each reaction type
        predictions = {}
        for reaction_type, head in self.reaction_heads.items():
            predictions[reaction_type] = head(encoded)

        # Estimate confidence
        confidence = (
            self._estimate_confidence(features, predictions)
            if return_confidence
            else None
        )

        return predictions, confidence

    def predict_single(
        self, brain_response: torch.Tensor, reaction_type: ReactionType
    ) -> ReactionPrediction:
        """Predict a single reaction type with full metadata."""
        predictions, confidence = self.forward(brain_response, return_confidence=True)

        pred = predictions[reaction_type.value]
        conf = confidence[reaction_type.value] if confidence else 0.5

        return ReactionPrediction(
            reaction_type=reaction_type,
            score=pred.item(),
            confidence=conf.item() if torch.is_tensor(conf) else conf,
        )

    def predict_all(self, brain_response: torch.Tensor) -> List[ReactionPrediction]:
        """Predict all reaction types."""
        predictions, confidence = self.forward(brain_response, return_confidence=True)

        results = []
        for rt in ReactionType:
            pred = predictions[rt.value]
            conf = confidence[rt.value] if confidence else 0.5

            results.append(
                ReactionPrediction(
                    reaction_type=rt,
                    score=pred.item() if torch.is_tensor(pred) else pred,
                    confidence=conf.item() if torch.is_tensor(conf) else conf,
                )
            )

        return results


class ReactionInterpreter:
    """
    Interprets reaction predictions into human-readable insights.
    """

    @staticmethod
    def summarize(predictions: List[ReactionPrediction]) -> str:
        """Create a text summary of reactions."""
        lines = ["Reaction Analysis:", "-" * 30]

        # Group by category
        attention_metrics = [
            ReactionType.ATTENTION,
            ReactionType.ENGAGEMENT,
            ReactionType.NOVELTY_RESPONSE,
        ]
        emotional_metrics = [
            ReactionType.EMOTION_VALENCE,
            ReactionType.EMOTION_AROUSAL,
            ReactionType.AESTHETIC_APPEAL,
        ]
        cognitive_metrics = [
            ReactionType.MEMORY_ENCODING,
            ReactionType.NARRATIVE_CURIOSITY,
            ReactionType.SOCIAL_CUE_RESPONSE,
        ]

        for group_name, metrics in [
            ("Attention & Engagement", attention_metrics),
            ("Emotional Response", emotional_metrics),
            ("Cognitive Processing", cognitive_metrics),
        ]:
            lines.append(f"\n{group_name}:")
            for rt in metrics:
                for pred in predictions:
                    if pred.reaction_type == rt:
                        bar = "#" * int(pred.score * 10) + "-" * (
                            10 - int(pred.score * 10)
                        )
                        lines.append(f"  {pred.describe():40s} [{bar}]")

        return "\n".join(lines)

    @staticmethod
    def get_dominant_reaction(
        predictions: List[ReactionPrediction],
    ) -> ReactionPrediction:
        """Get the most prominent reaction."""
        return max(predictions, key=lambda p: p.score * p.confidence)

    @staticmethod
    def suggest_content_type(reactions: List[ReactionPrediction]) -> str:
        """Suggest optimal content type based on reactions."""
        attention = (
            sum(
                p.score
                for p in reactions
                if p.reaction_type in [ReactionType.ATTENTION, ReactionType.ENGAGEMENT]
            )
            / 2
        )

        emotional = (
            sum(
                p.score
                for p in reactions
                if p.reaction_type
                in [ReactionType.EMOTION_VALENCE, ReactionType.EMOTION_AROUSAL]
            )
            / 2
        )

        cognitive = (
            sum(
                p.score
                for p in reactions
                if p.reaction_type
                in [ReactionType.NOVELTY_RESPONSE, ReactionType.NARRATIVE_CURIOSITY]
            )
            / 2
        )

        if emotional > 0.7 and attention < 0.5:
            return "emotional storytelling"
        elif cognitive > 0.6:
            return "educational/informational"
        elif attention > 0.7:
            return "fast-paced action"
        else:
            return "balanced narrative"
