# Data contract v1

`handover.scene.v1` is a JSON object with `units: "m"`:

- `object.id`: string identifier.
- `object.boxes`: object geometry as a union of oriented boxes.
- `object.usage_regions`: mapping from semantic region id to a list of boxes.
- `intent.human_region`: a key in `usage_regions`; `object_id`, `robot_region`,
  `hand` and `text2hoi_prompt` document the structured intent.
- `receiving_hand.center`, `receiving_hand.direction`: hand reference point and
  nonzero wrist-to-finger direction, in the object frame.
- `receiving_hand.boxes`: optional-to-the-algorithm geometry used by the viewer
  and simulator conversion; required by the provided CLI viewer.
- `gripper.max_opening_m`: maximum jaw aperture.
- `candidates`: ordered objects containing `id`, `T_object_gripper` and
  `approach_point_object` (precomputed approach-axis surface intersection).
- `utterance`, `provenance`: display text and source description.

A box has `center` (3), `half_extents` (3 positive numbers), `rotation` (3x3
proper rotation), and an optional `label`. Geometry is expressed in the object
frame. Transforms are 4x4 row-major JSON arrays used with column vectors:
`p_object = T_object_gripper @ p_gripper`. Local gripper Y is the closing axis;
local +Z is the approach direction. TCP is at the finger tips.

The width check projects all provided object boxes onto the closing axis. This
conservative proxy does not compute a local contact cross-section. The usage
check tests the supplied approach point; the separate benchmark affordance
check tests finger-volume intersection, so the two checks can differ.

`handover.selection.v1` contains `selected`, all evaluated `candidates`, `mode`,
`status`, `object_id`, and `provenance`. `selected` is null if no candidate is
feasible. Cost combines a unitless cosine and a distance in metres exactly as
in the paper; changing the geometry units changes ranking.

To replay in R2HandoverSim (installed separately):

```bash
r2handoversim from-intent --scene outputs/demo/hammer_scene.json \
  --selection outputs/demo/hammer_FS.json --output outputs/trial.json
r2handoversim demo --trial outputs/trial.json --headless
```

Conversion places the selected object/gripper relation at the demo's fixed UR5e
goal and positions the receiving hand relative to it. It does not plan an
arbitrary Cartesian target or claim neural hand-pose fidelity.
