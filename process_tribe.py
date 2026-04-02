"""
TRIBE v2 Processor - runs in a separate process to avoid threading issues on Windows.
Includes patches for Windows compatibility.
"""

import sys
import os
import json
import time
import ctypes
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def IsProcessAlive(pid):
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    except:
        return True


def patched_is_pid_alive(pid: int) -> bool:
    try:
        return IsProcessAlive(pid)
    except:
        return True


import exca.cachedict.inflight as inflight_module

inflight_module._is_pid_alive = patched_is_pid_alive


def main():
    if len(sys.argv) < 3:
        print(
            json.dumps(
                {"error": "Usage: python process_tribe.py <video_path> <output_path>"}
            )
        )
        sys.exit(1)

    video_path = sys.argv[1]
    output_path = sys.argv[2]

    result = {"success": False, "predictions": None, "error": None, "duration": 0}

    start = time.time()

    try:
        from tribev2 import TribeModel
        import pandas as pd
        from neuralset.events.transforms import ExtractAudioFromVideo, ChunkEvents
        from neuralset.events.utils import standardize_events

        print(f"Loading TRIBE v2 model...", file=sys.stderr)
        model = TribeModel.from_pretrained(
            "facebook/tribev2", cache_folder=str(script_dir / "cache")
        )

        print(f"Creating events dataframe...", file=sys.stderr)
        event = {
            "type": "Video",
            "filepath": video_path,
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

        print(f"Running predictions on {len(events)} events...", file=sys.stderr)
        predictions, segments = model.predict(events=events, verbose=True)

        print(f"Predictions shape: {predictions.shape}", file=sys.stderr)

        result["success"] = True
        result["predictions"] = predictions.tolist()
        result["segments_count"] = len(segments)

    except Exception as e:
        result["error"] = str(e)
        import traceback

        result["traceback"] = traceback.format_exc()

    result["duration"] = time.time() - start

    with open(output_path, "w") as f:
        json.dump(result, f)

    print(f"Done! Duration: {result['duration']:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
