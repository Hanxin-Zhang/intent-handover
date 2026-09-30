# Method and replay geometry audit — 2026-09-30

Audited method baseline: 15ac411 (0.5.1); fixes released in 0.6.0. Companion
benchmark code inspected read-only through 78e198d (0.8.0). The source
manuscript is `IROS26_3319_FI.pdf`, Sec. III-A/B.
This audit does not turn reconstructed replay into the paper's experiments.

## Findings and method changes

| Finding | Resolution / limit |
|---|---|
| Imported TCP lies on the approach surface, leaving proxy fingers behind it | Fit 18 mm insertion before selection and retain the original proposal |
| Whole-object width can reject a narrow handle or leave the local object between open fingers | New imports use the full local proxy pad footprint; old scenes keep global projection |
| Geometry changes can invalidate usage filtering and avoidance ranking | Recompute both on every final candidate, before FS/A1/A2/A3 selection |
| A stale surface annotation could conceal a changed axis | Local geometry requires a ray; the computed hit overrides annotations |
| Several TCP names refer to different physical origins | Explicit `parallel_jaw_tip` contract; reject unsupported input frames |
| The paper's hand-avoidance score is not a collision certificate | Preserve the written cosine-minus-distance score; no claim of collision-free execution |

The local section clips **all** object boxes against the pad X/Z window and
uses the outer Y envelope. It does not silently discard a wide disconnected
piece to obtain a feasible width. The two recorded contacts are proxy surface
extrema. Full finger/palm collision, friction, normals, force closure and
deformation are outside this selector's certificate.

## Required companion integration

No benchmark files were changed in this task. Its 0.8.0 `from_selection`
converter currently discards selected `width_m` and fixes `max_opening_m` at
0.085 m. `grasp_width` recomputes global projection unless an asset fit exists.
The real-asset path fits the chosen grasp again, potentially translating it
in X/Y/Z, and does not rerun method region filtering or rank all candidates.
It also shifts the hand with the modified object and moves old planning
status to `pre_asset_planning`. Consequently that replay cannot yet certify preservation of the
method's selected grasp or of paired receiver placement.

Version 0.8.0 now retains resolved scene/trajectory outputs, marks the receiver
as unpaired after retargeting, and makes repeated replay of a resolved scene
idempotent. These are useful provenance improvements. Method 0.6.0's
`audit-replay` reads those resolved scenes and fails explicitly on changed
grasp/width/frame or unpaired receiver state. Initial asset fitting still needs
the method integration described below.

The concrete interface requirements are:

1. Carry `selection.grasp_contract`, selected `width_m`, `width_source`,
   `proxy_contact`, `geometry_preparation`, mode and selected ID into trials
   and results. Read `scene.gripper.max_opening_m`, preserving user values.
   Reject unsupported policies rather than silently reverting to global width.
2. In proxy replay, use the selected local aperture consistently for rendering,
   planning and evaluation. It is aperture between pad planes in metres,
   **not** the nonlinear Robotiq linkage command.
3. Keep the calibrated method-TCP-to-asset-tool transform explicit. For a
   transform `T_method_asset` mapping asset-tool points into method-TCP
   coordinates, compose `T_object_asset = T_object_method @ T_method_asset`
   and `T_world_asset = T_world_method @ T_method_asset`. Record any
   width-dependent calibration. Do not reinterpret one frame as another.
4. Mesh-driven changes of physical grasp are different from a frame conversion.
   Fit the shared candidate set before method selection, or return each
   modified pose as a new candidate with an updated approach ray for method
   reselection. Rerun width, region intersection and avoidance ranking; checking
   only the previously selected candidate cannot preserve an argmin claim.
   Recompute delivery/planning after the final pose, while retaining the common
   receiver and object target for paired comparisons. Keep before/after poses,
   scores and constraint results in the record.
5. Never apply the asset adapter's insertion a second time merely because an
   already prepared candidate arrived. Measure whether fitting is needed in
   the declared frame. If an unvalidated post-selection repair is still used,
   report it as an adapted geometric replay with method validity/ranking
   unverified, not as the original FS outcome.

These requirements use the existing object-frame +Y/+Z conventions and do not
duplicate Robotiq USD calibration in the method package. For local proxy
candidate updates, the existing `intent-handover select` command recomputes
the complete candidate set. Exact mesh-based method width remains unsupported;
`proxy_contact` must not be relabelled as benchmark `grasp_contact` evidence.

## Paper fidelity still outside scope

- Original Multi-GraspLLM top-100 proposals, semantic segmentation and curated
  400-sequence intent-specific training data are unavailable in this config.
  The importer supplies 30 geometric proposals and authored regions.
- The neural path uses original Text2HOI weights and a coarse prediction/MANO
  bridge; no new weights are trained, and the full interaction refiner is absent.
- Speech/VLM calls, live calibrated body tracking and robot execution are not
  implemented by the offline method. Supplied intent and skeletal keypoints
  drive the available interfaces and execution formulas.
- Table I questionnaire results and Table II FS real-robot performance are
  reference results, not offline simulator outcomes. The reported 88%, 83.33%
  and 73.33% correspond to 132/150, 110/132 and 110/150 respectively. The paper
  provides no objective A1/A2/A3 simulation success rates to reconstruct.
