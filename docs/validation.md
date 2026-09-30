# Release validation — 2026-09-30

## 0.7.0 integration validation

- 54 CPU tests cover annotation frame conversion, numerical rotation repair,
  triangle ray intersections and clipped pad sections, independent asset contact
  validation, fixed receiver replay audits and earlier workflows. Python 3.11 /
  NumPy 1.26 and Python 3.10 / NumPy 2.2 runs are recorded locally.
- Restored all 6,827 local annotated candidates across 16 original objects and
  exported all 64 four-mode settings. Original OBJ triangles drive approach hits;
  this batch still uses explicitly labelled proxy pad widths and authored usage
  regions. All 64 selections survived companion conversion and method audit.
- Independently rechecked all 48 calibrated bottle candidates. Three final
  approach rays miss; FS/A2 reject another 13 for the supplied usage region.
  With the original bootstrap hand, FS/A1 choose candidate 42 (43.235 mm), while
  A2/A3 choose candidate 1 (30.958 mm). This is not a grasp success rate.
- Generated four fixed random left/right MANO receiver scenes (seed 27) in the
  companion and reran all four modes before conversion. All 16 inputs preserve
  selected pose/aperture, the original object mesh, full hand mesh/boxes and
  fixed receiver/object world poses in the method audit. FS/A1 now select
  candidate 4; A2/A3 select candidate 1. All 16 resolved Isaac trials also pass the same geometry audit. They
  fail the companion Stability stage: whole-mesh projected width exceeds
  85 mm, so planning is not attempted. Local contact aperture is not this
  whole-object metric; zero successes here must not be reported as successful
  planning or paper-result reproduction.
- Original candidates and mesh files, licensed MANO assets and derived replay
  records remain in ignored local outputs. The paper's 400 training trajectories,
  semantic surface masks and original experiment subset are not recovered;
  real-user and real-robot results are not inferred from these checks.

## 0.6.0 release validation

- 42 tests pass in Python 3.11 / NumPy 1.26.0 and in a fresh Python 3.10
  environment with NumPy 2.2.6 and the dataset extra. Coverage includes local
  pad geometry, final-pose constraints/ranking, replay changes, failed reruns,
  checkpoint/prediction integrity and meaningful CLI exit codes.
- A clean wheel installation ran all three CPU demos and four-mode ablations
  outside the checkout with no Torch, MANO, trimesh or simulator installed.
  After adding the dataset extra, it imported all 16 configured objects,
  reported the one missing cache entry and exported all 64 paired settings.
- Every imported setting has a feasible proxy candidate. Widths range from
  5.28 to 84.61 mm. All 128 selected proxy contacts lie on both an object-box
  surface and the corresponding inner finger plane, with residual below
  1e-12 m. FS/A2 selections satisfy the recomputed approach-point region test.
  These are geometry checks, **not simulation success rates**.
- Real original-weight Text2HOI inference ran 1,000 DDPM steps on CPU for the
  imported bottle (seed 0, right hand), decoded the local licensed MANO model,
  selected a grasp and produced an ergonomic delivery target. The output
  arrays are finite and prediction/checkpoint hashes are recorded. No GPU
  workload or Isaac Sim replay was started in this release validation.
- Read-only integration with benchmark 0.8.0 converted and evaluated the three
  bundled proxy scenes. All three passed its offline criteria and the new
  method replay audit. An imported bottle was correctly rejected by the audit:
  method local width 63.764 mm became benchmark global width 67.686 mm.
- Wheel and source distributions build successfully and pass `twine check`.
  The source archive includes documentation, examples and tests. Both archives
  include the required code licenses and exclude datasets, checkpoints, MANO,
  generated geometry and local outputs. Package requirements pass `pip check`.
- Companion replay still needs the integration in [geometry_audit.md](geometry_audit.md)
  for local aperture and original-asset method equivalence. No original-OBJ
  contact, force closure, frictional stability or paper user-study claim is
  inferred from these checks. All private/generated validation artifacts remain
  in ignored local output directories.

## 0.1.0 initial release

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

At version 0.1.0, MANO decoding was not yet connected. The full Text2HOI
refiner, live language model, real hardware, training and original paper results
remain outside the validation scope.

## 0.2.0 follow-up

- Ten CPU tests now pass, including the interleaved 6D rotation convention,
  object-frame invariance and palm-normal flipping.
- Decoded the actual H2O coarse output with locally supplied MANO using Python
  3.11, NumPy 1.26, SMPL-X 0.1.28 and Chumpy 0.70.
- Grasp selection on the decoded hand produced a valid result. The exported
  scene/selection pair ran in Isaac Sim, showing the decoded mesh and evaluating
  its skeletal collision proxies. The bottle example passed all active criteria.
- MANO models and generated hand meshes are excluded from the source release.
- Version 0.2.0 wheel installed independently; all three CPU demos ran from
  outside the source directory.

## 0.3.0 paper-detail follow-up

- Fifteen CPU tests pass, including ray/surface intersection, incorrect supplied
  surface annotations, comfortable radius/height, 15-degree extension, pose
  composition, forward sign and antipodal minimum-angle rotation.
- The authored seated-receiver skeleton produced a full delivery target. The
  companion benchmark solved this target with numerical pose IK, generated a
  collision-checked path, and replayed it successfully in Isaac Sim 5.0.
- The source PDF's Fig. 3 and Sec. III-B formulas were visually checked; explicit
  frame/axis/position-anchor conventions are recorded in `paper_details.md`.
- Version 0.3.0 wheels were built and the new delivery/planning integration was
  exercised outside both source trees using independently installed packages.

## 0.4.0 configured-data follow-up

- Eighteen CPU tests pass, including YAML default resolution, exact cached-point
  preservation, source hashing, missing-cache-entry reporting and input rejection.
- The original main config selected han. Imported all 16 existing PLY point
  clouds (8192 points each) plus their cached 1024-point inputs without rescaling.
  Reported the stale eyeglasses4 entry. Original files/cache were not modified.
- Ran a real 1000-step original-weight Text2HOI prediction on the imported
  binoculars cloud with a left-hand prompt; decoded with local MANO and selected
  a grasp. The full original object cloud survived conversion and Isaac replay.
- The 0.4.0 wheel's dataset import and cross-package conversion/evaluation ran
  outside both source directories. Data/derived geometry remain excluded from Git.

## 0.5.0 runnable-workflow follow-up

- Twenty-three tests pass, including structured-intent rejection, paired ablation
  exports, failed-run status replacement and corrupt-download preservation.
- The one-command pipeline verified all three original checkpoint hashes, ran
  1000 diffusion steps on CUDA, decoded local MANO and selected a bottle grasp.
  Its manifest converted directly to an Isaac Sim mesh-collision replay; all
  active demo criteria passed and screenshot/animated USD exports completed.
- Reimported all 16 configured objects with complete demo region catalogs and
  exported all 64 FS/A1/A2/A3 selections plus the experiment manifest.
- Reproduced Chumpy 0.70's isolated-build missing-pip failure with modern pip;
  verified the documented no-build-isolation/no-deps installation path.
- Built and independently installed the 0.5.0 wheel. Structured-intent selection,
  catalog prompts, checkpoint verification and paired-ablation exports ran
  outside the source directories and connected to the installed benchmark.
