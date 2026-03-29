"""
Main Pipeline - Ties everything together for easy usage.
"""

import torch
from typing import Optional, Dict, List, Union
from pathlib import Path

from .tribe_wrapper import TribePersonaWrapper
from .persona_encoder import PersonaEncoder, PersonaTraits, PersonaLibrary
from .reaction_predictor import ReactionPredictor, ReactionPrediction, ReactionType
from .fusion_module import PersonaFusionModule, BrainRegionMapper


class PersonaReactionPipeline:
    """
    Complete pipeline for persona-based reaction prediction.

    Usage:
        pipeline = PersonaReactionPipeline()
        pipeline.load_models()

        # Define persona
        persona = PersonaLibrary.get_persona("analytical")

        # Predict reactions
        reactions = pipeline.predict(
            video_path="content.mp4",
            persona=persona
        )

        print(pipeline.summarize_reactions(reactions))
    """

    def __init__(
        self,
        device: Optional[str] = None,
        persona_embedding_dim: int = 64,
        brain_hidden_dim: int = 512,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.persona_embedding_dim = persona_embedding_dim
        self.brain_hidden_dim = brain_hidden_dim

        # Models (loaded lazily)
        self.tribe_wrapper: Optional[TribePersonaWrapper] = None
        self.persona_encoder: Optional[PersonaEncoder] = None
        self.fusion_module: Optional[PersonaFusionModule] = None
        self.reaction_predictor: Optional[ReactionPredictor] = None
        self.brain_mapper: Optional[BrainRegionMapper] = None

        self._models_loaded = False

    def load_models(
        self, load_tribe: bool = True, pretrained_weights_path: Optional[str] = None
    ):
        """
        Load all required models.

        Args:
            load_tribe: Whether to load TRIBE v2 (requires HuggingFace auth)
            pretrained_weights_path: Path to trained persona-adapted weights
        """
        print("Loading models...")

        # Initialize persona encoder
        self.persona_encoder = PersonaEncoder(
            input_dim=14,
            embedding_dim=self.persona_embedding_dim,
            hidden_dims=[128, 128],
        ).to(self.device)

        # Initialize fusion module
        self.fusion_module = PersonaFusionModule(
            brain_dim=self.brain_hidden_dim,
            persona_dim=self.persona_embedding_dim,
            fusion_dim=self.brain_hidden_dim,
        ).to(self.device)

        # Initialize reaction predictor
        self.reaction_predictor = ReactionPredictor(
            brain_dim=self.brain_hidden_dim, hidden_dim=self.brain_hidden_dim
        ).to(self.device)

        # Initialize brain region mapper
        self.brain_mapper = BrainRegionMapper(num_vertices=20480, hidden_dim=128).to(
            self.device
        )

        # Optionally load TRIBE v2
        if load_tribe:
            try:
                self.tribe_wrapper = TribePersonaWrapper(
                    num_persona_dims=self.persona_embedding_dim,
                    brain_hidden_dim=self.brain_hidden_dim,
                )
                self.tribe_wrapper.load_tribe(cache_folder="./cache")
                self.tribe_wrapper.to(self.device)
                print("[OK] TRIBE v2 loaded")
            except Exception as e:
                print(f"[!] Could not load TRIBE v2: {e}")
                print("  Install with: pip install tribev2")
                print("  And run: huggingface-cli login")

        # Optionally load pretrained persona weights
        if pretrained_weights_path:
            self._load_pretrained(pretrained_weights_path)

        self._models_loaded = True
        print("[OK] Pipeline ready!")

    def _load_pretrained(self, path: str):
        """Load pretrained model weights."""
        checkpoint = torch.load(path, map_location=self.device)

        if "persona_encoder" in checkpoint:
            self.persona_encoder.load_state_dict(checkpoint["persona_encoder"])
        if "fusion_module" in checkpoint:
            self.fusion_module.load_state_dict(checkpoint["fusion_module"])
        if "reaction_predictor" in checkpoint:
            self.reaction_predictor.load_state_dict(checkpoint["reaction_predictor"])

            print(f"[OK] Loaded pretrained weights from {path}")

    def save_models(self, path: str):
        """Save model weights."""
        checkpoint = {
            "persona_encoder": self.persona_encoder.state_dict(),
            "fusion_module": self.fusion_module.state_dict(),
            "reaction_predictor": self.reaction_predictor.state_dict(),
        }
        torch.save(checkpoint, path)
        print(f"✓ Saved weights to {path}")

    def predict(
        self,
        video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        text_path: Optional[str] = None,
        persona: Optional[Union[PersonaTraits, str]] = None,
        stimuli_features: Optional[torch.Tensor] = None,
        return_brain_regions: bool = False,
    ) -> Dict:
        """
        Predict reactions for given stimuli and persona.

        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            text_path: Path to text file
            persona: PersonaTraits object or string name from PersonaLibrary
            stimuli_features: Pre-extracted stimuli features (skip TRIBE)
            return_brain_regions: Include brain region activations

        Returns:
            Dictionary with predictions, confidence, and optional brain regions
        """
        if not self._models_loaded:
            raise RuntimeError("Models not loaded. Call load_models() first.")

        # Handle persona
        if isinstance(persona, str):
            persona = PersonaLibrary.get_persona(persona)
        elif persona is None:
            # Use analytical persona as default
            persona = PersonaLibrary.get_persona("analytical")

        # Encode persona
        persona_vector = self.persona_encoder.encode_from_persona(persona)
        persona_vector = persona_vector.to(self.device)

        # Get brain response
        if stimuli_features is not None:
            brain_response = stimuli_features.to(self.device)
        elif self.tribe_wrapper is not None:
            result = self.tribe_wrapper.predict_brain_response(
                video_path=video_path,
                audio_path=audio_path,
                text_path=text_path,
                persona_embedding=persona_vector,
                return_raw=True,
            )
            brain_response = result["brain_response"].to(self.device)
        else:
            raise ValueError("Either stimuli_features or loaded TRIBE v2 required")

        # Apply persona fusion
        fused = self.fusion_module(brain_response, persona_vector)

        # Predict reactions
        predictions, confidence = self.reaction_predictor(
            fused["fused"], return_confidence=True
        )

        # Convert to ReactionPrediction objects
        reaction_list = []
        for rt in ReactionType:
            reaction_list.append(
                ReactionPrediction(
                    reaction_type=rt,
                    score=predictions[rt.value].item(),
                    confidence=confidence[rt.value].item(),
                )
            )

        result = {
            "reactions": reaction_list,
            "persona": persona,
            "raw_predictions": predictions,
            "confidence": confidence,
        }

        # Optionally include brain region analysis
        if return_brain_regions:
            result["brain_regions"] = self.brain_mapper.get_region_importance(
                brain_response
            )

        return result

    def predict_from_brain_features(
        self, brain_features: torch.Tensor, persona: Union[PersonaTraits, str]
    ) -> List[ReactionPrediction]:
        """
        Predict reactions from pre-computed brain features.

        Useful when you have brain features from another source.
        """
        if isinstance(persona, str):
            persona = PersonaLibrary.get_persona(persona)

        persona_vector = self.persona_encoder.encode_from_persona(persona)
        persona_vector = persona_vector.to(self.device)
        brain_features = brain_features.to(self.device)

        fused = self.fusion_module(brain_features, persona_vector)
        predictions, confidence = self.reaction_predictor(
            fused["fused"], return_confidence=True
        )

        return [
            ReactionPrediction(
                reaction_type=rt,
                score=predictions[rt.value].item(),
                confidence=confidence[rt.value].item(),
            )
            for rt in ReactionType
        ]

    def compare_personas(
        self,
        video_path: Optional[str] = None,
        personas: Optional[List[Union[PersonaTraits, str]]] = None,
        stimuli_features: Optional[torch.Tensor] = None,
    ) -> Dict[str, List[ReactionPrediction]]:
        """
        Compare reactions across different personas.

        Returns:
            Dict mapping persona name to their reactions
        """
        if personas is None:
            personas = list(PersonaLibrary.PERSONAS.keys())

        results = {}
        for persona in personas:
            results[str(persona) if isinstance(persona, str) else "custom"] = (
                self.predict(
                    video_path=video_path,
                    persona=persona,
                    stimuli_features=stimuli_features,
                )["reactions"]
            )

        return results

    @staticmethod
    def summarize_reactions(reactions: List[ReactionPrediction]) -> str:
        """Create a text summary of reactions."""
        lines = ["=" * 50, "REACTION PREDICTION SUMMARY", "=" * 50, ""]

        # Sort by score
        sorted_reactions = sorted(reactions, key=lambda r: r.score, reverse=True)

        lines.append("Top Reactions:")
        for r in sorted_reactions[:3]:
            bar = "#" * int(r.score * 10) + "-" * (10 - int(r.score * 10))
            conf = f"(conf: {r.confidence:.2f})"
            lines.append(f"  {r.describe():35s} [{bar}] {conf}")

        lines.append("\nAll Reactions:")
        for r in reactions:
            lines.append(f"  {r.describe()}")

        lines.append("")

        return "\n".join(lines)

    def generate_insights(
        self, reactions: List[ReactionPrediction], persona: PersonaTraits
    ) -> Dict[str, str]:
        """
        Generate human-readable insights from reactions.
        """
        insights = {}

        # Overall engagement
        avg_engagement = (
            sum(
                r.score
                for r in reactions
                if r.reaction_type in [ReactionType.ATTENTION, ReactionType.ENGAGEMENT]
            )
            / 2
        )

        if avg_engagement > 0.7:
            insights["engagement"] = (
                "High engagement expected - content is likely to capture and hold attention"
            )
        elif avg_engagement > 0.4:
            insights["engagement"] = (
                "Moderate engagement - content will hold interest but may not be captivating"
            )
        else:
            insights["engagement"] = (
                "Low engagement expected - may struggle to maintain attention"
            )

        # Emotional response
        valence = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.EMOTION_VALENCE
            ),
            0.5,
        )
        arousal = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.EMOTION_AROUSAL
            ),
            0.5,
        )

        if valence > 0.6 and arousal > 0.6:
            insights["emotional"] = (
                "Strong positive emotional response expected - highly enjoyable content"
            )
        elif valence > 0.6:
            insights["emotional"] = "Positive emotional response - pleasant experience"
        elif valence < 0.4 and arousal > 0.6:
            insights["emotional"] = (
                "Intense but potentially negative emotional response - may be distressing"
            )
        elif valence < 0.4:
            insights["emotional"] = "Neutral to negative emotional tone"
        else:
            insights["emotional"] = "Calm, neutral emotional response"

        # Learning potential
        memory = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.MEMORY_ENCODING
            ),
            0.5,
        )
        curiosity = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.NARRATIVE_CURIOSITY
            ),
            0.5,
        )

        if memory > 0.6 and curiosity > 0.5:
            insights["learning"] = (
                "High learning potential - content is memorable and promotes curiosity"
            )
        elif memory > 0.5:
            insights["learning"] = (
                "Good memory encoding - information likely to be retained"
            )
        else:
            insights["learning"] = (
                "Low retention expected - may need reinforcement for learning"
            )

        # Social relevance
        social = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.SOCIAL_CUE_RESPONSE
            ),
            0.5,
        )
        if social > 0.6:
            insights["social"] = (
                "Strong social relevance - person will be attuned to social dynamics"
            )
        elif social < 0.4:
            insights["social"] = (
                "Low social sensitivity - content's social elements may be overlooked"
            )

        # Novelty
        novelty = next(
            (
                r.score
                for r in reactions
                if r.reaction_type == ReactionType.NOVELTY_RESPONSE
            ),
            0.5,
        )
        if novelty > 0.7:
            insights["novelty"] = (
                "High novelty response - content feels fresh and surprising"
            )
        elif novelty < 0.3:
            insights["novelty"] = "Low novelty - content feels familiar/predictable"

        return insights

    def demo_without_tribe(self, persona: PersonaTraits) -> Dict:
        """
        Demo the system without TRIBE v2 by generating simulated brain features.
        Useful for testing and development.
        """
        # Generate random brain features
        brain_features = torch.randn(1, self.brain_hidden_dim).to(self.device)

        persona_vector = self.persona_encoder.encode_from_persona(persona)
        persona_vector = persona_vector.to(self.device)

        fused = self.fusion_module(brain_features, persona_vector)
        predictions, confidence = self.reaction_predictor(
            fused["fused"], return_confidence=True
        )

        reaction_list = [
            ReactionPrediction(
                reaction_type=rt,
                score=predictions[rt.value].item(),
                confidence=confidence[rt.value].item(),
            )
            for rt in ReactionType
        ]

        return {
            "reactions": reaction_list,
            "persona": persona,
            "note": "Demo mode - using simulated brain features",
        }
