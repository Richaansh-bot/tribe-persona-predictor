"""
Fusion Module - Combines TRIBE brain features with persona embeddings.
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Tuple


class PersonaFusionModule(nn.Module):
    """
    Fuse brain response features with persona embeddings using
    cross-attention and gating mechanisms.
    """

    def __init__(
        self,
        brain_dim: int = 512,
        persona_dim: int = 64,
        fusion_dim: int = 512,
        num_heads: int = 8,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.brain_dim = brain_dim
        self.persona_dim = persona_dim
        self.fusion_dim = fusion_dim

        # Project inputs to common dimension
        self.brain_proj = nn.Linear(brain_dim, fusion_dim)
        self.persona_proj = nn.Linear(persona_dim, fusion_dim)

        # Cross-attention: brain attends to persona
        self.cross_attention_bp = nn.MultiheadAttention(
            embed_dim=fusion_dim, num_heads=num_heads, dropout=dropout, batch_first=True
        )

        # Cross-attention: persona attends to brain
        self.cross_attention_pb = nn.MultiheadAttention(
            embed_dim=fusion_dim, num_heads=num_heads, dropout=dropout, batch_first=True
        )

        # Gating mechanism
        self.gate_network = nn.Sequential(
            nn.Linear(fusion_dim * 2, fusion_dim), nn.Sigmoid()
        )

        # Fusion layers
        self.fusion_layer = nn.Sequential(
            nn.LayerNorm(fusion_dim * 2),
            nn.Linear(fusion_dim * 2, fusion_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(fusion_dim, fusion_dim),
        )

        # Residual connection
        self.residual_scale = nn.Parameter(torch.tensor(0.1))

    def forward(
        self,
        brain_features: torch.Tensor,
        persona_embedding: torch.Tensor,
        return_attention_weights: bool = False,
    ) -> Dict[str, torch.Tensor]:
        """
        Fuse brain features with persona.

        Args:
            brain_features: Shape (batch, brain_dim) or (batch, seq, brain_dim)
            persona_embedding: Shape (batch, persona_dim)
            return_attention_weights: Return cross-attention weights

        Returns:
            fused: Fused representation
            attention_weights: Optional cross-attention weights
        """
        # Track original shape
        original_shape = brain_features.shape
        is_sequential = brain_features.dim() == 3

        # Project to fusion dimension
        brain_proj = self.brain_proj(brain_features)
        persona_proj = self.persona_proj(persona_embedding)

        if is_sequential:
            # Expand persona for sequential brain features
            persona_expanded = persona_proj.unsqueeze(1)  # (batch, 1, fusion_dim)
        else:
            persona_expanded = persona_proj.unsqueeze(
                1
            )  # (batch, 1, fusion_dim) for attention

        # Layer norm before attention
        brain_proj = nn.functional.layer_norm(brain_proj, (self.fusion_dim,))
        persona_proj = nn.functional.layer_norm(persona_expanded, (self.fusion_dim,))

        # Cross-attention: brain attends to persona
        if is_sequential:
            # For sequential data: (batch, seq, dim)
            attn_bp, weights_bp = self.cross_attention_bp(
                brain_proj, persona_expanded, persona_expanded
            )
        else:
            # For non-sequential: expand to sequence length of 1
            brain_expanded = brain_proj.unsqueeze(1)
            attn_bp, weights_bp = self.cross_attention_bp(
                brain_expanded, persona_expanded, persona_expanded
            )
            attn_bp = attn_bp.squeeze(1)

        # Cross-attention: persona attends to brain
        if is_sequential:
            attn_pb, weights_pb = self.cross_attention_pb(
                persona_expanded, brain_proj, brain_proj
            )
            attn_pb = attn_pb.squeeze(1)  # (batch, fusion_dim)
        else:
            attn_pb = persona_proj.squeeze(1)

        # Concatenate and gate
        concatenated = torch.cat([attn_bp, attn_pb], dim=-1)
        gate = self.gate_network(concatenated)

        # Expand gate to match concatenated dimensions
        gate_expanded = gate.repeat(1, 2)  # (batch, fusion_dim * 2)

        # Apply gating
        fused = concatenated * gate_expanded

        # Final fusion transformation
        fused = self.fusion_layer(fused)

        # Residual connection
        if not is_sequential:
            fused = fused + self.residual_scale * brain_proj
        else:
            fused = fused + self.residual_scale * brain_proj.mean(dim=1)

        result = {"fused": fused}

        if return_attention_weights:
            result["attention_brain_to_persona"] = weights_bp
            result["attention_persona_to_brain"] = weights_pb

        return result


class BrainRegionMapper(nn.Module):
    """
    Maps raw brain responses to interpretable brain regions.
    Useful for understanding which brain areas are activated.
    """

    # Approximate cortical region vertex indices for fsaverage5 (~20k vertices)
    REGIONS = {
        "frontal": (0, 4000),
        "parietal": (4000, 8000),
        "temporal": (8000, 12000),
        "occipital": (12000, 16000),
        "cingulate": (16000, 18000),
        "insula": (18000, 20000),
        "subcortical": (20000, 20480),  # Limited subcortical in fsaverage5
    }

    def __init__(self, num_vertices: int = 20480, hidden_dim: int = 128):
        super().__init__()

        self.num_vertices = num_vertices
        self.regions = list(self.REGIONS.keys())

        # Per-region projectors
        self.region_projectors = nn.ModuleDict()
        for region in self.regions:
            start, end = self.REGIONS[region]
            self.region_projectors[region] = nn.Sequential(
                nn.Linear(end - start, hidden_dim), nn.ReLU()
            )

        # Cross-region attention
        self.region_attention = nn.MultiheadAttention(
            embed_dim=hidden_dim, num_heads=4, batch_first=True
        )

    def forward(self, brain_response: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Extract region-level activations.

        Args:
            brain_response: Shape (batch, num_vertices) or (batch, seq, num_vertices)

        Returns:
            region_activations: Dict mapping region name to activation vector
        """
        is_sequential = brain_response.dim() == 3

        if is_sequential:
            # Temporal mean first
            brain_response = brain_response.mean(dim=1)

        # Extract each region
        region_features = []
        for region in self.regions:
            start, end = self.REGIONS[region]
            region_data = brain_response[:, start:end]
            projected = self.region_projectors[region](region_data)
            region_features.append(projected)

        # Stack regions: (batch, num_regions, hidden_dim)
        region_stack = torch.stack(region_features, dim=1)

        # Cross-region attention
        attended, _ = self.region_attention(region_stack, region_stack, region_stack)

        # Return dict of region activations
        return {region: attended[:, i] for i, region in enumerate(self.regions)}

    def get_region_importance(self, brain_response: torch.Tensor) -> Dict[str, float]:
        """Get importance scores for each region."""
        activations = self.forward(brain_response)

        importance = {}
        for region, activation in activations.items():
            importance[region] = activation.mean().item()

        # Normalize
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}

        return importance
