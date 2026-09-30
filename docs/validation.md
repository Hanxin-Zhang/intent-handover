# Release validation — 2026-09-30

- Seven CPU unit tests passed: usage ablation, aperture filtering, scoring,
  malformed inputs, rigid transforms, oriented-box intersections and neural
  point-cloud preprocessing.
- All three bundled grasp-selection demos ran and exported HTML, JSON and
  point-cloud files.
- Original Text2HOI H2O contact, PointNet and TextHOM checkpoints loaded with
  strict key matching. A real 1000-step, one-frame right-hand inference ran on
  CUDA with the bundled bottle proxy cloud and seed 0. All output arrays were
  finite. Verified file hashes are in `verified_weights.json`.
- Neural test environment: Python 3.11, PyTorch 2.7.0+cu126, NumPy 1.26.0,
  NVIDIA RTX 4070. This verifies execution, not grasp quality on proxy geometry.
- Editable installation and wheel build succeeded. Installed demos ran from
  outside the source directory; wheel contents included demo assets and the
  upstream Text2HOI license.
- A generated scene/selection pair was converted by the companion benchmark
  and successfully replayed in Isaac Sim 5.0.

The full Text2HOI refiner, MANO decoding, live language model, real hardware,
training and original paper results were not validated by this release.
