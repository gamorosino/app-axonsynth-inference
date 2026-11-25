<h1 align="center">axonsynth-inference</h1>

<p align="center">
  Segments axons in a 3D light-sheet microscopy volume with the AxonSynth three_class_v2 MONAI 3D U-Net, after optional resampling to isotropic voxels, and outputs a binary axon mask and probability map.
</p>

<p align="center">
  <a href="https://github.com/brainlife/abcd-spec"><img src="https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg" alt="ABCD Spec v1.1"></a>
  <a href="https://doi.org/10.25663/brainlife.app.974"><img src="https://img.shields.io/badge/Brainlife-brainlife.app.974-blue.svg" alt="Run on brainlife.io"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-see_LICENSE-lightgrey.svg" alt="License"></a>
</p>

## At a glance

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Segments axons in a 3D light-sheet microscopy volume with the AxonSynth three_class_v2 MONAI 3D U-Net, after optional resampling to isotropic voxels, and outputs a binary axon mask and probability map.**

Optionally resamples an anisotropic LSM NIfTI to isotropic model space (default 0.8 micron, axis order 2,0,1), then runs sliding-window inference with the bundled three_class_v2 checkpoint (background, axon shell, axon interior) and collapses shell and interior into a thresholded binary foreground. Use it for automated axon segmentation of LSM data. It runs on GPU when available and falls back to CPU unless require_cuda is set.

| | |
|---|---|
| **Inputs** | `neuro/microscopy/nifti` |
| **Outputs** | `neuro/parcellation/volume` |
| **Container** | `gamorosino/app-axonsynth-inference:0.1` |
| **Resources** | 4 GB memory · 1 h walltime |
| **Run it** | [doi.org/10.25663/brainlife.app.974](https://doi.org/10.25663/brainlife.app.974) |

#### Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `input_volume` | `neuro/microscopy/nifti` | yes | Raw or already-prepared 3D LSM microscopy volume (NIfTI). |

#### Outputs

| Output | Datatype | Description |
|---|---|---|
| `segmentation` | `neuro/parcellation/volume` | Predicted binary axon segmentation (AxonSynth three_class_v2, shell+interior collapsed to foreground) as parc.nii.gz, with label.json, plus the foreground probability map and inference metadata as extra files. |

<details>
<summary><b>Parameters</b> (12)</summary>

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

## Running the App

### On brainlife.io

Open the App at [doi.org/10.25663/brainlife.app.974](https://doi.org/10.25663/brainlife.app.974), choose `neuro/microscopy/nifti` from your project, set the parameters and press **Execute**. The results are saved to your project as `neuro/parcellation/volume`.

### Locally

You need [Singularity/Apptainer](https://apptainer.org/) (the App runs in `gamorosino/app-axonsynth-inference:0.1`), [`jq`](https://jqlang.github.io/jq/).

1. Clone this repository.
2. Create `config.json` with the paths to your inputs and the parameters:

   ```json
   {
       "input_volume": "/path/to/input_volume/input_volume",
       "skip_prepare": false,
       "target_spacing": 0.8,
       "axis_order": "2,0,1",
       "assume_source_units_micron": true,
       "roi_size": 128,
       "sw_batch_size": 4,
       "overlap": 0.5,
       "threshold": 0.5,
       "stitch_device": "model",
       "output_profile": "binary_focused",
       "require_cuda": false,
       "additional_thresholds": ""
   }
   ```

3. Run `./main`.

## Troubleshooting

- **no output produced**: Check the log for errors in the prepare or inference step (e.g. wrong axis_order or missing GPU with require_cuda).

## Pipeline

1. **Prepare** (skippable via `skip_prepare`): `prepare_lsm_full.py` resamples
   an anisotropic source NIfTI to isotropic model space (default 0.8um,
   axis order 2,0,1).
2. **Infer**: `infer_lsm.py` runs sliding-window inference with the baked-in
   `three_class_v2` checkpoint and writes the foreground probability map and
   thresholded binary mask.

## Citing

If you use this App, please cite it, the software it builds on and brainlife.io:

- axonsynth-inference. brainlife.io App. [doi:10.25663/brainlife.app.974](https://doi.org/10.25663/brainlife.app.974)
- Hayashi S, Caron BA, Heinsfeld AS, et al. brainlife.io: a decentralized and open-source cloud platform to support neuroscience research. *Nature Methods* 21:809–813 (2024). [doi:10.1038/s41592-024-02237-2](https://doi.org/10.1038/s41592-024-02237-2)
- Avesani P, McPherson B, Hayashi S, et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. *Scientific Data* 6:69 (2019). [doi:10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

## Authors

- Gabriele Amorosino

## License

See [LICENSE](LICENSE).
