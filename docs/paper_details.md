# Paper implementation and reproduction boundaries

Source: **Intent-Handover: Grounding Language in Human-Usage Regions for
Trustworthy Robot-to-Human Handovers**, supplied manuscript `IROS26_3319_FI.pdf`,
Sec. III-A/B and Fig. 3. This is a runnable reconstruction, not recovered
experiment code or a reproduction of the reported user-study measurements.

| Paper detail | Code | Remaining difference |
|---|---|---|
| Width and human-usage constraints, Sec. III-A.3 | `core.select_grasp` | Original triangle meshes and explicit width conventions are supported; human-usage regions still require supplied labels |
| Approach-axis intersection `x_int` | `geometry.approach_intersection`, `mesh_geometry.mesh_approach_intersection` | Exact ray/triangle or ray/OBB intersection; legacy supplied points still accepted |
| Minimize cosine minus hand/gripper distance | `core.select_grasp` | Metres, equal coefficients as written in the paper; no additional learned ranking |
| FS/A1/A2/A3 | `core.MODES` | First feasible input candidate is the explicit A2/A3 tie policy |
| Shoulder/torso centre and comfortable reach radius | `execution.delivery_target` | Calibrated keypoints supplied offline; no live MediaPipe/RealSense pipeline |
| 15° extension and minimum-angle direction alignment | `execution.axis_rotation`, `minimum_rotation` | Explicit axis/facing conventions below |
| World/robot/object/gripper transform composition | `execution.delivery_target` | Calibration must be supplied; identity world-to-robot is the default |

## Run the execution formulas

From this repository:

```bash
intent-handover demo --object hammer
intent-handover delivery \
  --scene outputs/demo/hammer_scene.json \
  --selection outputs/demo/hammer_FS.json \
  --skeleton examples/seated_receiver.json \
  --output outputs/ergonomic_delivery.json
```

The example contains authored seated-person keypoints, not participant data.
Input `handover.skeleton.v1` uses metres, world +Z up, left/right shoulder,
elbow and wrist coordinates, desk height, a facing hint and an extension axis.
All points must already be calibrated into the same world frame.

The implementation follows the paper's formulas:

- `c_sh = (left_shoulder + right_shoulder) / 2`.
- `c_t = [c_sh.x, c_sh.y, (c_sh.z + z_desk) / 2]`.
- `l_ua = ||elbow - c_sh||`, `l_fa = ||wrist - elbow||`.
- `r_star = sqrt(l_ua**2 + l_fa**2)`, `P = c_t + r_star * e_f`.
- `e_h = R_extension(15 degrees) * normalize(wrist - elbow)`.
- Minimum-angle `R` aligns the stored predicted wrist-to-middle-finger direction
  with `e_h`.

In particular, the upper-arm length uses the **shoulder midpoint**, as printed
in the manuscript, not the ipsilateral shoulder.

## Explicit coordinate choices

The equations do not fully specify all implementation conventions. This release
uses these documented choices rather than inferring undocumented calibration:

1. `facing_hint_world` selects the forward sign of the horizontal perpendicular
   to the shoulder axis. An ambiguous hint is rejected.
2. `extension_axis_world` is a signed world-frame unit axis perpendicular to the
   forearm. Positive extension uses the right-hand rule; default magnitude is
   15°. This specifies the wrist flexion/extension plane without inferring it
   from shoulder points alone.
3. The canonical hand direction is the stored hand direction in object
   coordinates. The minimum rotation rotates the entire hand/object/grasp
   configuration together. Rotation around that direction is resolved by the
   minimum-angle rule, with a deterministic perpendicular axis at the 180° tie.
4. `P` anchors the **object origin**. The predicted hand centre retains its
   offset from that origin; it is not independently snapped to `P`.
5. `T_a_b` maps frame b to a. Thus `T_world_gripper = T_world_object *
   T_object_gripper`, and `T_robot_gripper = T_robot_world * T_world_gripper`.

Output `handover.delivery.v1` includes these poses, intermediate quantities,
keypoints and target direction for diagnosis. A target is not proof of robot
reachability. The benchmark's numerical IK and collision checker can reject it.

## Send the target to Isaac Sim

In the separate benchmark's environment, with its optional planning extra:

```bash
python -m pip install -e '.[planning]'
r2handoversim from-intent \
  --scene /path/to/intent-handover/outputs/demo/hammer_scene.json \
  --selection /path/to/intent-handover/outputs/demo/hammer_FS.json \
  --delivery /path/to/intent-handover/outputs/ergonomic_delivery.json \
  --seed 0 --output outputs/ergonomic_trial.json
r2handoversim demo --trial outputs/ergonomic_trial.json --headless \
  --screenshot --animation --output outputs/ergonomic_isaac
```

The receiving configuration stays fixed at the computed world-frame target.
The robot starts at its home configuration; the target does not get moved to a
preselected reachable joint pose. Supplied body keypoints and target direction
are visual references in Isaac Sim, not additional human-body colliders.

The 400 curated training sequences, trained intent-specific model and live
speech/vision stack are not recreated. Sec. III-A defines N grasp candidates;
it does not prescribe top-100. A separately located local Panda annotation
archive now supplies 6,827 proposals for 16 objects, but its exact correspondence
to the paper experiment subset has not been established.
The neural route continues to use original Text2HOI weights, per release scope.

## Local data now connected (0.4.0)

The original han config's 16 available object point clouds and neural input
cache can now be imported directly. This restores those local object inputs;
original triangle meshes, grasp/region annotations and split labels remain
unavailable in that config. See [dataset import and provenance](dataset.md).

## Geometry audit (0.6.0)

New imports prepare inserted, centred candidates and measure local proxy pad
width before applying the paper's region constraint and avoidance score. Existing
scenes retain global projection unless they opt in. Separate original OBJ assets
were found outside the configured point-cloud layout; they remain local and are
handled by the companion asset adapter. See [geometry audit](geometry_audit.md)
for the frame contract, remaining paper gaps and required replay revalidation.

## Original candidates and calibrated assets

The annotation importer explicitly converts the Panda base to the method
finger-tip frame using source control points. Its optional Y centring occurs
before selection; it adds no proxy insertion. Tiny source rotation errors are
projected onto SO(3) with the raw values retained. The avoidance reference can
be the measured pad centre instead of an implicit CAD origin.

For real-asset replay, the companion prepares all candidates first. The method
independently checks the final mesh width, approach intersection, usage region
and cost before selecting. A sampled receiving hand must also be fixed before
selection; moving or replacing it afterwards invalidates the result. See
[the integration contract](geometry_audit.md). The randomized receiver protocol
is an explicit benchmark condition, not a recovered paper participant trial.
