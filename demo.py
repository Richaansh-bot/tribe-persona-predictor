"""
Quick demo script - run without TRIBE v2 for testing.
"""

from tribev2_persona import PersonaReactionPipeline
from tribev2_persona.models import PersonaLibrary, ReactionType


def demo():
    """Run a quick demo of the pipeline."""

    print("=" * 60)
    print("PERSONA-BASED REACTION PREDICTOR DEMO")
    print("=" * 60)

    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = PersonaReactionPipeline(device="cpu")
    pipeline.load_models(load_tribe=False)  # Demo mode without TRIBE

    # Demo with different personas
    personas = ["analytical", "creative", "emotional", "social"]

    print("\n2. Comparing reactions across personas...")
    print("-" * 60)

    for persona_name in personas:
        print(f"\n>>> Persona: {persona_name.upper()}")

        # Get predictions
        result = pipeline.demo_without_tribe(PersonaLibrary.get_persona(persona_name))

        # Print summary
        print(pipeline.summarize_reactions(result["reactions"]))

        # Print insights
        insights = pipeline.generate_insights(result["reactions"], result["persona"])

        print("Key Insights:")
        for key, value in insights.items():
            print(f"  * {key.capitalize()}: {value}")

    # Custom persona demo
    print("\n" + "=" * 60)
    print("CUSTOM PERSONA EXAMPLE")
    print("=" * 60)

    custom_persona = PersonaLibrary.create_custom(
        openness=0.9,
        conscientiousness=0.5,
        extraversion=0.3,
        learning_style="visual",
        emotional_range="high",
    )

    result = pipeline.demo_without_tribe(custom_persona)
    print("\nCustom Persona Traits:")
    print(f"  Openness: {custom_persona.openness}")
    print(f"  Conscientiousness: {custom_persona.conscientiousness}")
    print(f"  Visual Learner: {custom_persona.visual_learner}")
    print(f"  Emotional Sensitivity: {custom_persona.emotional_sensitivity}")

    print("\nPredicted Reactions:")
    print(pipeline.summarize_reactions(result["reactions"]))

    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("""
To use with real brain predictions:
1. Install TRIBE v2: pip install tribev2
2. Authenticate: huggingface-cli login
3. Load TRIBE: pipeline.load_models(load_tribe=True)
4. Predict: pipeline.predict(video_path="your_video.mp4", persona="analytical")
    """)


if __name__ == "__main__":
    demo()
