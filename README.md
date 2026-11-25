# axonsynth-inference

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Segments axons in a 3D light-sheet microscopy volume with the AxonSynth three_class_v2 MONAI 3D U-Net, after optional resampling to isotropic voxels, and outputs a binary axon mask and probability map.**

Optionally resamples an anisotropic LSM NIfTI to isotropic model space (default 0.8 micron, axis order 2,0,1), then runs sliding-window inference with the bundled three_class_v2 checkpoint (background, axon shell, axon interior) and collapses shell and interior into a thresholded binary foreground. Use it for automated axon segmentation of LSM data. It runs on GPU when available and falls back to CPU unless require_cuda is set.

| | |
|---|---|
| 📥 **Inputs** | `neuro/microscopy/nifti` |
| 📤 **Outputs** | `neuro/parcellation/volume` |
| 🐳 **Container** | `gamorosino/app-axonsynth-inference:0.1` |
| ⚙️ **Resources** | 4 GB memory · 1 h walltime |
| 🔗 **Run it** | [doi.org/10.25663/brainlife.app.974](https://doi.org/10.25663/brainlife.app.974) |

#### 📥 Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `input_volume` | `neuro/microscopy/nifti` | yes | Raw or already-prepared 3D LSM microscopy volume (NIfTI). |

#### 📤 Outputs

| Output | Datatype | Description |
|---|---|---|
| `segmentation` | `neuro/parcellation/volume` | Predicted binary axon segmentation (AxonSynth three_class_v2, shell+interior collapsed to foreground) as parc.nii.gz, with label.json, plus the foreground probability map and inference metadata as extra files. |

<details>
<summary><b>⚙️ Parameters</b> (12)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `skip_prepare` | boolean | `false` | Skip the anisotropic-to-isotropic resample step; use only when input_volume is already isotropic at model spacing (0.8um by default). |
| `target_spacing` | number | `0.8` | Target isotropic voxel size in microns for the prepare step. Ignored if skip_prepare is true. |
| `axis_order` | string | `2,0,1` | Comma-separated permutation of 0,1,2 mapping model axes to source axes for the prepare step. Ignored if skip_prepare is true. |
| `assume_source_units_micron` | boolean | `true` | Treat source NIfTI header zoom values as microns when the header does not declare micron units. Ignored if skip_prepare is true. |
| `roi_size` | number | `128` | Isotropic sliding-window ROI size used during inference. |
| `sw_batch_size` | number | `4` | Sliding-window inference batch size. |
| `overlap` | number | `0.5` | Sliding-window overlap fraction (0 to <1). |
| `threshold` | number | `0.5` | Foreground probability threshold applied to produce the binary segmentation. |
| `stitch_device` | string | `model` | Device used to stitch sliding-window logits: 'model' (default, same device as the model) or 'cpu' (for volumes that exceed GPU memory when stitched). |
| `output_profile` | string | `binary_focused` | 'binary_focused' (default) writes only the collapsed foreground probability/mask; 'full' additionally writes the three-class argmax, shell, and interior masks. |
| `require_cuda` | boolean | `false` | Fail instead of silently falling back to CPU when no GPU is available on the compute resource. |
| `additional_thresholds` | string |  | Comma-separated LABEL=VALUE pairs for extra binary masks at additional probability thresholds, e.g. '0p94=0.94'. Empty means none. |

</details>

<!-- brainlife-app:end -->

3D axon segmentation inference on a light-sheet microscopy (LSM) volume using
[lincbrain/axonsynth](https://github.com/lincbrain/axonsynth)'s primary
`three_class_v2` MONAI 3D U-Net (background / axon shell / axon interior,
collapsed to a binary foreground for the main output). Runs with or without a
GPU: inference falls back to CPU automatically unless `require_cuda` is set.

## Inputs

- `input_volume` (neuro/microscopy/nifti) -- raw or already-prepared 3D LSM
  volume.

## Outputs

- `segmentation` (neuro/parcellation/volume) -- `parc.nii.gz` (binary axon
  mask) + `label.json`, plus `pred_prob.nii.gz` (foreground probability map)
  and `inference_metadata.json` as extra files in the same output. Chains
  directly into `app-seg-eval-metrics`'s `moving_parc` input.

## Pipeline

1. **Prepare** (skippable via `skip_prepare`): `prepare_lsm_full.py` resamples
   an anisotropic source NIfTI to isotropic model space (default 0.8um,
   axis order 2,0,1).
2. **Infer**: `infer_lsm.py` runs sliding-window inference with the baked-in
   `three_class_v2` checkpoint and writes the foreground probability map and
   thresholded binary mask.

## Usage

Brainlife.io: run via `braise-app-run`/`braise-app-pipeline` (once registered
with `braise-app-create`), or the web UI.

Locally (outside brainlife): copy `config.json.example` to `config.json`,
fill in real file paths, then run `./main` from this directory. `main` pulls
its own container (`singularity exec --nv docker://...`) -- no local install
of torch/monai needed, only Singularity itself. The `--nv` flag is a no-op
when no NVIDIA driver is present, so the same container runs CPU-only too.

Entrypoint: `main.py`

## Authors

- Gabriele Amorosino <ga24643@eid.utexas.edu>

## License

MIT, see `LICENSE`, except `prepare_lsm_full.py` and `infer_lsm.py`, which
are vendored verbatim from
[lincbrain/axonsynth](https://github.com/lincbrain/axonsynth) at commit
[`335a354`](https://github.com/lincbrain/axonsynth/tree/335a354ad6681c85c1c3ffabc75325d08e1285f2/inference).
That upstream repo has no LICENSE file of its own. The baked-in
`three_class_v2` checkpoint (`three_class_v2_best_model.pt`) is likewise from
that project; its own `repro/checkpoints/three_class_v2_best.json` marks it
`"availability": "local_only"` -- it is not otherwise redistributed by the
upstream project.
