"""
Core wrapper that combines TRIBE v2 with persona-specific predictions.
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, List, Union
import numpy as np

try:
    from tribev2 import TribeModel

    TRIBE_AVAILABLE = True
except ImportError:
    TRIBE_AVAILABLE = False
    print("Warning: TRIBE v2 not installed. Install with: pip install tribev2")


class TribePersonaWrapper(nn.Module):
    """
    Wraps TRIBE v2 and adds persona-specific adaptation.

    Instead of outputting the "average" brain response, this wrapper
    applies persona-specific transformations to the base predictions.
    """

    def __init__(
        self,
        tribe_model: Optional["TribeModel"] = None,
        num_persona_dims: int = 64,
        brain_hidden_dim: int = 512,
        use_tribe_cache: bool = True,
    ):
        super().__init__()

        self.tribe_model = tribe_model
        self.num_persona_dims = num_persona_dims
        self.brain_hidden_dim = brain_hidden_dim
        self.use_tribe_cache = use_tribe_cache

        self.tribe_cache = {}

        # Persona-conditioned modulation network
        # Modulates TRIBE outputs based on persona embeddings
        self.persona_modulator = nn.Sequential(
            nn.Linear(num_persona_dims, brain_hidden_dim),
            nn.GELU(),
            nn.Linear(brain_hidden_dim, brain_hidden_dim),
            nn.Sigmoid(),  # Gating mechanism
        )

        # Attention-based persona fusion
        self.persona_attention = nn.MultiheadAttention(
            embed_dim=brain_hidden_dim, num_heads=8, dropout=0.1
        )

        # Layer norms
        self.pre_ln = nn.LayerNorm(brain_hidden_dim)
        self.post_ln = nn.LayerNorm(brain_hidden_dim)

    def forward(
        self, stimuli_features: torch.Tensor, persona_embedding: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            stimuli_features: Shape (batch, seq_len, brain_hidden_dim)
                             Features extracted from TRIBE v2
            persona_embedding: Shape (batch, num_persona_dims)
                              Persona trait vector
        """
        # Get modulation gates from persona
        gates = self.persona_modulator(persona_embedding)  # (batch, brain_hidden_dim)

        # Apply persona-conditioned modulation
        modulated = stimuli_features * gates.unsqueeze(1)

        # Self-attention with persona conditioning
        modulated = self.pre_ln(modulated)
        attn_out, _ = self.persona_attention(
            modulated, modulated, modulated, key_padding_mask=None
        )
        modulated = self.post_ln(modulated + attn_out)

        return modulated

    def predict_brain_response(
        self,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        text_path: Optional[str] = None,
        persona_embedding: Optional[torch.Tensor] = None,
        return_raw: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Predict brain response for given stimuli with persona conditioning.

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            text_path: Path to text file
            persona_embedding: Optional persona traits (if None, uses average)
            return_raw: If True, also returns raw TRIBE predictions

        Returns:
            Dictionary with 'brain_response', 'raw_response', 'persona_conditioned'
        """
        if not TRIBE_AVAILABLE:
            raise RuntimeError(
                "TRIBE v2 not installed. Install with: pip install tribev2"
            )

        if self.tribe_model is None:
            raise RuntimeError("TribeModel not loaded. Call load_tribe() first.")

        # Get events dataframe from stimuli
        df = self.tribe_model.get_events_dataframe(
            video_path=video_path, audio_path=audio_path, text_path=text_path
        )

        # Get raw TRIBE predictions
        raw_preds, segments = self.tribe_model.predict(events=df)
        raw_response = torch.from_numpy(raw_preds).float()

        if raw_response.dim() == 2:
            raw_response = raw_response.unsqueeze(0)

        if persona_embedding is None:
            # Return average response (TRIE v2 default)
            return {
                "brain_response": raw_response,
                "raw_response": raw_response if return_raw else None,
                "persona_conditioned": False,
            }

        # Ensure persona_embedding is properly shaped
        if persona_embedding.dim() == 1:
            persona_embedding = persona_embedding.unsqueeze(0)

        # Project raw response to brain_hidden_dim if needed
        if raw_response.shape[-1] != self.brain_hidden_dim:
            projector = nn.Linear(raw_response.shape[-1], self.brain_hidden_dim).to(
                raw_response.device
            )
            features = projector(raw_response)
        else:
            features = raw_response

        # Apply persona conditioning
        conditioned_response = self.forward(features, persona_embedding)

        # Project back to original dimension
        if conditioned_response.shape[-1] != raw_response.shape[-1]:
            back_projector = nn.Linear(
                self.brain_hidden_dim, raw_response.shape[-1]
            ).to(conditioned_response.device)
            brain_response = back_projector(conditioned_response)
        else:
            brain_response = conditioned_response

        return {
            "brain_response": brain_response,
            "raw_response": raw_response if return_raw else None,
            "persona_conditioned": True,
            "persona_gates": gates if self.training else None,
        }

    def load_tribe(self, cache_folder: str = "./cache"):
        """Load TRIBE v2 model from HuggingFace."""
        if not TRIBE_AVAILABLE:
            raise RuntimeError("TRIBE v2 not installed.")
        self.tribe_model = TribeModel.from_pretrained(
            "facebook/tribev2", cache_folder=cache_folder
        )
        return self

    @classmethod
    def from_pretrained(cls, persona_dims: int = 64, **kwargs):
        """Create and optionally load TRIBE v2."""
        instance = cls(num_persona_dims=persona_dims, **kwargs)
        return instance
