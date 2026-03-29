"""
Persona Encoding System - Converts user traits into embedding vectors.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import numpy as np


@dataclass
class PersonaTraits:
    """Container for persona trait data."""

    # Big Five Personality Traits (O, C, E, A, N)
    openness: float = 0.5  # 0-1
    conscientiousness: float = 0.5  # 0-1
    extraversion: float = 0.5  # 0-1
    agreeableness: float = 0.5  # 0-1
    neuroticism: float = 0.5  # 0-1

    # Learning & Processing Styles
    visual_learner: float = 0.5  # Preference for visual input
    auditory_learner: float = 0.5  # Preference for auditory input
    reading_learner: float = 0.5  # Preference for text input

    # Emotional Response Tendencies
    emotional_sensitivity: float = 0.5  # How strongly they respond emotionally
    arousal_level: float = 0.5  # Baseline arousal/activation
    valence_bias: float = 0.5  # Positive(1) vs Negative(0) bias

    # Cognitive Traits
    attention_span: float = 0.5  # How long they stay engaged
    abstract_reasoning: float = 0.5  # Preference for abstract vs concrete
    creativity: float = 0.5  # Creative thinking tendency

    # Demographics (optional)
    age_group: Optional[int] = None  # 1=young, 2=adult, 3=middle, 4=senior
    cultural_background: Optional[str] = None

    def to_vector(self) -> np.ndarray:
        """Convert traits to numpy vector."""
        traits = [
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism,
            self.visual_learner,
            self.auditory_learner,
            self.reading_learner,
            self.emotional_sensitivity,
            self.arousal_level,
            self.valence_bias,
            self.attention_span,
            self.abstract_reasoning,
            self.creativity,
        ]
        if self.age_group:
            age_encoding = {
                1: [1, 0, 0, 0],  # Young
                2: [0, 1, 0, 0],  # Adult
                3: [0, 0, 1, 0],  # Middle
                4: [0, 0, 0, 1],  # Senior
            }
            traits.extend(age_encoding.get(self.age_group, [0, 0, 0, 0]))
        return np.array(traits, dtype=np.float32)

    @classmethod
    def from_mbti(cls, mbti_type: str) -> "PersonaTraits":
        """
        Create persona from MBTI type.
        MBTI: I/E + N/S + T/F + J/P
        """
        mapping = {
            "I": ("extraversion", 0.3),
            "E": ("extraversion", 0.7),
            "N": ("openness", 0.8),  # Intuitive
            "S": ("openness", 0.4),  # Sensing
            "T": ("abstract_reasoning", 0.7),  # Thinking
            "F": ("emotional_sensitivity", 0.7),  # Feeling
            "J": ("conscientiousness", 0.7),  # Judging
            "P": ("conscientiousness", 0.4),  # Perceiving
        }

        traits = {}
        for i, (dim, default) in enumerate(
            [(0.5, 0.5), (0.5, 0.5), (0.5, 0.5), (0.5, 0.5)]
        ):
            if i < len(mbti_type):
                char = mbti_type[i]
                if char in mapping:
                    key, val = mapping[char]
                    traits[key] = val
            else:
                traits["extraversion"] = 0.5  # Default

        return cls(**traits)

    @classmethod
    def from_dict(cls, data: Dict) -> "PersonaTraits":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class PersonaEncoder(nn.Module):
    """
    Neural network encoder for persona traits.
    Converts raw trait values into dense embedding vectors.
    """

    def __init__(
        self,
        input_dim: int = 14,  # 14 base traits (without age encoding)
        embedding_dim: int = 64,
        hidden_dims: List[int] = [128, 128],
        dropout: float = 0.1,
    ):
        super().__init__()

        self.input_dim = input_dim
        self.embedding_dim = embedding_dim

        # Build encoder network
        layers = []
        prev_dim = input_dim

        for hidden_dim in hidden_dims:
            layers.extend(
                [
                    nn.Linear(prev_dim, hidden_dim),
                    nn.LayerNorm(hidden_dim),
                    nn.GELU(),
                    nn.Dropout(dropout),
                ]
            )
            prev_dim = hidden_dim

        layers.append(nn.Linear(prev_dim, embedding_dim))

        self.encoder = nn.Sequential(*layers)

        # Brain region specialization learned weights
        self.region_weights = nn.Parameter(torch.ones(embedding_dim) / embedding_dim)

    def forward(self, traits: torch.Tensor) -> torch.Tensor:
        """
        Encode persona traits to embedding.

        Args:
            traits: Shape (batch, input_dim) or (input_dim,) raw trait values

        Returns:
            embedding: Shape (batch, embedding_dim)
        """
        if traits.dim() == 1:
            traits = traits.unsqueeze(0)

        embedding = self.encoder(traits)

        # Apply learned region weighting
        embedding = embedding * self.region_weights.unsqueeze(0)

        return embedding

    def encode_from_persona(self, persona: PersonaTraits) -> torch.Tensor:
        """Encode a PersonaTraits object."""
        trait_vector = torch.from_numpy(persona.to_vector())
        return self.forward(trait_vector)

    def encode_from_mbti(self, mbti: str) -> torch.Tensor:
        """Encode from MBTI type string."""
        persona = PersonaTraits.from_mbti(mbti)
        return self.encode_from_persona(persona)


class PersonaLibrary:
    """
    Pre-built persona templates for common user types.
    """

    PERSONAS = {
        "analytical": PersonaTraits(
            openness=0.7,
            conscientiousness=0.8,
            extraversion=0.3,
            agreeableness=0.5,
            neuroticism=0.3,
            visual_learner=0.6,
            auditory_learner=0.5,
            reading_learner=0.7,
            emotional_sensitivity=0.3,
            arousal_level=0.4,
            valence_bias=0.5,
            attention_span=0.8,
            abstract_reasoning=0.9,
            creativity=0.5,
        ),
        "creative": PersonaTraits(
            openness=0.9,
            conscientiousness=0.4,
            extraversion=0.6,
            agreeableness=0.6,
            neuroticism=0.5,
            visual_learner=0.8,
            auditory_learner=0.6,
            reading_learner=0.4,
            emotional_sensitivity=0.7,
            arousal_level=0.7,
            valence_bias=0.6,
            attention_span=0.5,
            abstract_reasoning=0.8,
            creativity=0.95,
        ),
        "emotional": PersonaTraits(
            openness=0.6,
            conscientiousness=0.5,
            extraversion=0.5,
            agreeableness=0.7,
            neuroticism=0.7,
            visual_learner=0.5,
            auditory_learner=0.7,
            reading_learner=0.4,
            emotional_sensitivity=0.9,
            arousal_level=0.6,
            valence_bias=0.4,  # Slightly negative bias
            attention_span=0.5,
            abstract_reasoning=0.5,
            creativity=0.6,
        ),
        "pragmatic": PersonaTraits(
            openness=0.4,
            conscientiousness=0.9,
            extraversion=0.5,
            agreeableness=0.6,
            neuroticism=0.4,
            visual_learner=0.5,
            auditory_learner=0.5,
            reading_learner=0.7,
            emotional_sensitivity=0.3,
            arousal_level=0.5,
            valence_bias=0.5,
            attention_span=0.7,
            abstract_reasoning=0.4,
            creativity=0.3,
        ),
        "social": PersonaTraits(
            openness=0.7,
            conscientiousness=0.5,
            extraversion=0.9,
            agreeableness=0.8,
            neuroticism=0.4,
            visual_learner=0.4,
            auditory_learner=0.8,
            reading_learner=0.5,
            emotional_sensitivity=0.6,
            arousal_level=0.7,
            valence_bias=0.7,  # Positive bias
            attention_span=0.6,
            abstract_reasoning=0.5,
            creativity=0.6,
        ),
        "tech_savvy": PersonaTraits(
            openness=0.8,
            conscientiousness=0.7,
            extraversion=0.4,
            agreeableness=0.5,
            neuroticism=0.3,
            visual_learner=0.7,
            auditory_learner=0.4,
            reading_learner=0.6,
            emotional_sensitivity=0.4,
            arousal_level=0.6,
            valence_bias=0.5,
            attention_span=0.7,
            abstract_reasoning=0.8,
            creativity=0.7,
        ),
    }

    @classmethod
    def get_persona(cls, name: str) -> PersonaTraits:
        """Get a pre-built persona by name."""
        if name.lower() not in cls.PERSONAS:
            raise ValueError(
                f"Unknown persona: {name}. Available: {list(cls.PERSONAS.keys())}"
            )
        return cls.PERSONAS[name.lower()]

    @classmethod
    def list_personas(cls) -> List[str]:
        """List available persona names."""
        return list(cls.PERSONAS.keys())

    @classmethod
    def create_custom(
        cls,
        openness: float = 0.5,
        conscientiousness: float = 0.5,
        extraversion: float = 0.5,
        agreeableness: float = 0.5,
        neuroticism: float = 0.5,
        learning_style: str = "balanced",  # visual, auditory, reading, balanced
        emotional_range: str = "moderate",  # low, moderate, high
    ) -> PersonaTraits:
        """Create a custom persona with simplified parameters."""

        learning_map = {
            "visual": (0.8, 0.4, 0.4),
            "auditory": (0.4, 0.8, 0.4),
            "reading": (0.4, 0.4, 0.8),
            "balanced": (0.5, 0.5, 0.5),
        }
        visual, auditory, reading = learning_map.get(learning_style, (0.5, 0.5, 0.5))

        emotional_map = {"low": 0.3, "moderate": 0.5, "high": 0.8}
        emotional = emotional_map.get(emotional_range, 0.5)

        return PersonaTraits(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism,
            visual_learner=visual,
            auditory_learner=auditory,
            reading_learner=reading,
            emotional_sensitivity=emotional,
            arousal_level=0.5,
            valence_bias=0.5,
            attention_span=0.5,
            abstract_reasoning=openness,
            creativity=openness,
        )
