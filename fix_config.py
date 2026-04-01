"""Fix TRIBE v2 config for Windows and load model"""

import os
from pathlib import Path

# Find the downloaded config
cache_dir = Path(
    "C:/Users/giris/.cache/huggingface/hub/models--facebook--tribev2/snapshots"
)
snapshots = list(cache_dir.glob("*"))
if snapshots:
    config_path = snapshots[0] / "config.yaml"
    ckpt_path = snapshots[0] / "best.ckpt"

    # Read and fix the config
    with open(config_path, "r") as f:
        config_content = f.read()

    # Replace PosixPath with Windows-compatible path handling
    config_content = config_content.replace(
        "!!python/object/apply:pathlib.PosixPath", "# PosixPath"
    )
    config_content = config_content.replace(
        "!!python/object:pathlib.PosixPath", "# PosixPath"
    )

    # Save fixed config
    fixed_config_path = config_path.parent / "config_fixed.yaml"
    with open(fixed_config_path, "w") as f:
        f.write(config_content)

    print(f"Config fixed: {fixed_config_path}")
    print(f"Checkpoint: {ckpt_path}")
    print(
        f"Checkpoint size: {os.path.getsize(ckpt_path) / (1024 * 1024 * 1024):.2f} GB"
    )
