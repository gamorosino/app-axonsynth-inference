#!/usr/bin/env python3
"""brainlife.io entrypoint: AxonSynth 3D axon segmentation inference.

Runs `prepare_lsm_full` (optional anisotropic -> isotropic resampling) and
`infer_lsm` (sliding-window MONAI U-Net inference) against the baked-in
three_class_v2 checkpoint, then writes the result as a
neuro/parcellation/volume output (parc.nii.gz + label.json).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import infer_lsm
from prepare_lsm_full import prepare_lsm_full

CONFIG_PATH = "config.json"
OUTPUT_DIR = Path("segmentation")
CHECKPOINT_PATH = Path("/opt/axonsynth/checkpoints/three_class_v2_best_model.pt")


def _axis_order(raw: str) -> tuple[int, int, int]:
    parts = tuple(int(token.strip()) for token in raw.split(","))
    if len(parts) != 3:
        raise ValueError(f"axis_order must have 3 comma-separated ints, got {raw!r}")
    return parts


def _additional_thresholds(raw: str) -> list[str]:
    raw = raw.strip()
    return [token.strip() for token in raw.split(",") if token.strip()]


def main() -> None:
    with open(CONFIG_PATH) as f:
        config = json.load(f)

    input_path = Path(config["input_volume"])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if bool(config.get("skip_prepare", False)):
        prepared_path = input_path
    else:
        prepared_path = OUTPUT_DIR / "prepared_input.nii.gz"
        prepare_lsm_full(
            input_path,
            prepared_path,
            target_spacing=float(config.get("target_spacing", 0.8)),
            axis_order=_axis_order(str(config.get("axis_order", "2,0,1"))),
            assume_source_units_micron=bool(config.get("assume_source_units_micron", True)),
        )

    infer_dir = OUTPUT_DIR / "infer"
    infer_dir.mkdir(parents=True, exist_ok=True)

    argv = [
        "--input", str(prepared_path),
        "--checkpoint", str(CHECKPOINT_PATH),
        "--output-dir", str(infer_dir),
        "--segmentation-mode", "three_class_shell_interior",
        "--roi-size", str(int(config.get("roi_size", 128))),
        "--sw-batch-size", str(int(config.get("sw_batch_size", 4))),
        "--overlap", str(float(config.get("overlap", 0.5))),
        "--threshold", str(float(config.get("threshold", 0.5))),
        "--stitch-device", str(config.get("stitch_device", "model")),
        "--output-profile", str(config.get("output_profile", "binary_focused")),
        "--no-save-input",
    ]
    if bool(config.get("require_cuda", False)):
        argv.append("--require-cuda")
    for entry in _additional_thresholds(str(config.get("additional_thresholds", ""))):
        argv.extend(["--additional-threshold", entry])

    infer_lsm.main(argv)

    output_prefix = infer_lsm.default_output_prefix(prepared_path)
    pred_path = infer_dir / f"{output_prefix}_pred.nii.gz"
    prob_path = infer_dir / f"{output_prefix}_pred_prob.nii.gz"
    metadata_path = infer_dir / f"{output_prefix}_inference_metadata.json"

    shutil.copyfile(pred_path, OUTPUT_DIR / "parc.nii.gz")
    if prob_path.exists():
        shutil.copyfile(prob_path, OUTPUT_DIR / "pred_prob.nii.gz")
    if metadata_path.exists():
        shutil.copyfile(metadata_path, OUTPUT_DIR / "inference_metadata.json")

    label = [
        {
            "name": "background",
            "voxel_value": 0,
            "desc": "predicted background (not axon)",
        },
        {
            "name": "axon_foreground",
            "voxel_value": 1,
            "desc": (
                "predicted axon foreground (AxonSynth three_class_v2, "
                "shell+interior collapsed)"
            ),
        },
    ]
    with open(OUTPUT_DIR / "label.json", "w") as f:
        json.dump(label, f, indent=2)


if __name__ == "__main__":
    main()
