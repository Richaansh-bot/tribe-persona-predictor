"""
Debug script to test TRIBE v2 directly - full pipeline test.
"""

import sys
import os
import time
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

print("=" * 60)
print("TRIBE v2 FULL DEBUG SCRIPT")
print("=" * 60)

print("\n[1] Importing TRIBE v2...")
start = time.time()
try:
    from tribev2 import TribeModel

    print(f"[OK] TRIBE v2 imported in {time.time() - start:.1f}s")
except ImportError as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

print("\n[2] Loading TRIBE v2 model...")
start = time.time()
cache_dir = script_dir / "cache"
try:
    model = TribeModel.from_pretrained("facebook/tribev2", cache_folder=str(cache_dir))
    print(f"[OK] Model loaded in {time.time() - start:.1f}s")
except Exception as e:
    print(f"[FAIL] {e}")
    sys.exit(1)

print("\n[3] Creating events dataframe...")
start = time.time()
try:
    import pandas as pd
    from neuralset.events.transforms import ExtractAudioFromVideo, ChunkEvents
    from neuralset.events.utils import standardize_events

    test_video = script_dir / "uploads" / "2b3419cb.mp4"
    print(f"    Video: {test_video}")

    event = {
        "type": "Video",
        "filepath": str(test_video),
        "start": 0,
        "timeline": "default",
        "subject": "default",
    }
    events = pd.DataFrame([event])

    transforms = [
        ExtractAudioFromVideo(),
        ChunkEvents(event_type_to_chunk="Audio", max_duration=60, min_duration=30),
        ChunkEvents(event_type_to_chunk="Video", max_duration=60, min_duration=30),
    ]

    events = standardize_events(events)
    for transform in transforms:
        events = transform(events)
    events = standardize_events(events)

    print(f"[OK] Events created in {time.time() - start:.1f}s")
    print(f"    Shape: {events.shape}")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n[4] Running predict() - this may take several minutes...")
print("    (Will show progress below)")
start = time.time()

try:
    result = model.predict(events=events, verbose=True)
    elapsed = time.time() - start
    print(f"\n[OK] predict() completed in {elapsed:.1f}s ({elapsed / 60:.1f} minutes)")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n[FAIL] predict() failed after {elapsed:.1f}s: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n[5] Analyzing results...")
if result is None:
    print("[FAIL] predict() returned None!")
    sys.exit(1)

brain_preds, segments = result
print(f"    brain_preds type: {type(brain_preds)}")
print(f"    brain_preds shape: {brain_preds.shape}")
print(f"    brain_preds min: {brain_preds.min():.4f}")
print(f"    brain_preds max: {brain_preds.max():.4f}")
print(f"    brain_preds mean: {brain_preds.mean():.4f}")
print(f"    segments count: {len(segments)}")

print("\n[6] Testing reaction generation...")
try:
    from server import generate_reactions_from_tribe, get_brain_region_mapping

    reactions = generate_reactions_from_tribe(
        brain_preds, "analytical", "test_video.mp4"
    )
    print(f"    Generated {len(reactions)} reactions:")
    for r in reactions:
        print(f"      {r.type}: {r.score:.3f} (confidence: {r.confidence:.3f})")

    brain_regions = get_brain_region_mapping(brain_preds)
    print(f"    Generated {len(brain_regions)} brain regions:")
    for br in brain_regions:
        print(f"      {br.name}: {br.activation:.3f}")

except Exception as e:
    print(f"[FAIL] {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60)
print("DEBUG COMPLETE - ALL TESTS PASSED!")
print("=" * 60)
