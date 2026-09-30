# Changelog

## 0.5.0

- Add a one-command original-weight Text2HOI/MANO/selection pipeline with stage
  tracking, optional structured intent and optional ergonomic delivery.
- Consume structured intent responses and build prompts from actual scene catalogs.
- Export paired FS/A1/A2/A3 experiments for bundled or locally imported objects.
- Verify checkpoint SHA-256 before use/replacement and reject partial downloads.
- Fix fresh-environment Chumpy installation guidance and missing region catalogs.

## 0.4.0

- Read the original main/dataset YAML config and import locally available han data.
- Preserve source point clouds, cached neural inputs, coordinates, scale and hashes.
- Report missing cached objects without inventing replacements.
- Generate explicitly labelled grasp/hand/region demo annotations for real objects.
- Display imported point clouds and preserve them through MANO decoding.

## 0.3.0

- Implement Sec. III-B ergonomic delivery from calibrated skeletal keypoints,
  including comfortable reach, wrist extension, minimal rotation and pose chains.
- Compute approach-axis surface intersections for bundled grasp candidates.
- Add a portable skeleton example and a paper-to-code implementation map.

## 0.2.0

- Connect original H2O Text2HOI predictions to grasp selection through optional
  local MANO decoding and correct object-frame conversion.
- Export predicted hand mesh, skeletal proxies, palm normal and checkpoint
  provenance to the companion benchmark.
- Support legacy MANO files with scoped Python/NumPy compatibility fixes.
- Add coordinate-convention and normal-orientation tests.

## 0.1.0

- Initial CPU grasp-selection examples, structured prompts, standalone reports
  and original-weight coarse Text2HOI inference.
