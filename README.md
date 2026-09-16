# axonsynth-inference

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
