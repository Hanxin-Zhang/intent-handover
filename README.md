# Intent-Handover

Runnable core code for **Intent-Handover: Grounding Language in Human-Usage
Regions for Trustworthy Robot-to-Human Handovers**.

This release prioritizes working examples. Run three CPU demos with no
GPU, model download, MANO, ROS, or simulator. Each demo filters robot grasps by
gripper aperture and the intended human usage region, then ranks valid grasps
using `cos(robot_approach, hand_direction) - distance_m`.

Companion benchmark: [R2HandoverSim](https://github.com/Hanxin-Zhang/r2handoversim).

## Quick start

Python 3.10 or newer:

```bash
git clone https://github.com/Hanxin-Zhang/intent-handover.git
cd intent-handover
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
intent-handover demo
```

Open `outputs/demo/hammer_FS.html` (also screwdriver and bottle) in a browser.
Each example writes a scene JSON, ranked results JSON, object point cloud `.npy`, and a standalone HTML
visualization. No web server or CDN is needed. On Windows, activate with
`.venv\Scripts\activate`.

```bash
intent-handover demo --object hammer --mode A1 --output outputs/ablation
intent-handover select outputs/demo/hammer_scene.json --output outputs/custom
intent-handover prompt --instruction "I need to tighten a screw."
python -m pip install -e '.[dataset]'
python -m unittest discover -s tests -v
```

If an installed console command is unavailable, use `python -m intent_handover`
with the same arguments.

## Complete workflows

```bash
# Run all four method ablations on the three bundled objects:
intent-handover ablate --output outputs/ablation
# Apply a structured intent response:
intent-handover select outputs/demo/hammer_scene.json \
  --intent examples/hammer_intent.json --output outputs/intent
```

The experiment manifest connects directly to the benchmark's `from-experiment`
command for paired Isaac Sim comparisons. See [workflow commands](docs/workflows.md).

With the optional neural dependencies and local MANO installed,
`intent-handover pipeline` runs original-weight prediction, MANO decoding and
selection in one command. It verifies checkpoint hashes and exports a manifest
that the benchmark accepts through `from-pipeline`.
See [installation and the complete neural recipe](docs/neural_pipeline.md).

## Use the existing local dataset config

The original project defaults to `dataset: han`. Its available data contains
16 object point clouds, each with 8192 source points and 1024 cached points.
Import directly from that config:

```bash
python -m pip install -e '.[dataset]'
intent-handover dataset --config /path/to/Text2HOI/configs/config.yaml \
  --output outputs/han_dataset
```

This preserves original coordinates, names and dimensions, and produces neural
input clouds, viewable scenes, grasp-selection demos and a source manifest.
The generated hand, candidate grasps and receiving-zone labels are explicitly
marked as demo annotations. See [dataset setup and provenance](docs/dataset.md).

## Included functionality

| Component | Release behavior |
|---|---|
| Grasp selection | Executable NumPy implementation of width/usage filtering and avoidance cost |
| FS / A1 / A2 / A3 | Switch usage awareness and avoidance ranking independently; width remains enforced |
| Prompts | Authored structured-intent system prompt and examples, available through the `prompt` command |
| Text2HOI | Optional original-weight coarse DDPM inference; see [setup](docs/text2hoi.md) |
| Visualization | Standalone HTML with object, receiving hand and gripper geometry |
| Ergonomic delivery | Shoulder/elbow/wrist keypoints → comfortable radius, 15° extension and a world-frame target; see [paper details](docs/paper_details.md) |
| Predicted hand integration | Decode Text2HOI outputs with local MANO, select a grasp, and export the mesh/proxies to R2HandoverSim |

The default examples use **original procedural box geometry and fixed receiving
hand proxies**, not neural predictions or recovered paper trials. Prompt output
is ready to send to your chosen model; the demo does not make an API call.
The supplied region geometry is an annotation, not a segmentation inferred from
text. Bundled examples compute the first approach-ray intersection with the object
boxes and filter that surface point against the intended region. Legacy inputs
may still supply a surface annotation directly.

The optional neural adapter reuses the **original Text2HOI pretrained weights**;
there are no new Intent-Handover weights to download or train. It produces coarse
hand/object parameters and contact probabilities without the refiner. The new
`from-prediction` command decodes those parameters with your locally licensed
MANO models and runs grasp selection using that predicted hand. See
[the end-to-end recipe](docs/neural_pipeline.md). Default CPU demos still use
fixed hand proxies and do not require MANO.

## Use your own example

Edit a generated `*_scene.json`, or provide one matching [the data contract](docs/schema.md).
All coordinates are in metres in the object frame. Candidate transforms map
gripper coordinates into object coordinates. The gripper closes along local Y
and approaches along local +Z. Unknown regions, invalid rotations, zero hand
directions, and duplicate candidates fail with an explanatory error. If all
candidates fail, the output is `no_feasible_grasp` with no selected pose.

## Release scope

This repository extracts the scoring idea from the original DUM-E/Text2HOI
prototype and implements the missing lightweight constraints and interfaces.
The default gripper is a box proxy with an 85 mm aperture, not Panda or Robotiq
CAD. Geometric feasibility is simplified; no force closure, IK or trajectory
safety guarantee is implied by a selected grasp. A2/A3 choose the first feasible
candidate in input order, an explicit demo tie policy. The companion benchmark can solve a delivery target with numerical pose IK and
RRT-Connect using explicit collision proxies. Full speech/vision,
MediaPipe tracking, hardware control, training and user-study replication are
outside this release.

Original code is MIT; vendored Text2HOI retains its own MIT notice. No MANO
models, third-party dataset meshes, checkpoints or participant recordings are
bundled. See [THIRD_PARTY.md](THIRD_PARTY.md).

Paper/project: [Intent-Handover](https://robot-future.github.io/intent-handover/).

## Replay with original Isaac Sim assets

`ablate` also exports `replay.json`: paired FS/A1/A2/A3 settings, selected grasps,
and links to each scene and selection. It excludes real-robot statistics and
participant questionnaires; the paper does not report an objective simulation
success rate for these four method settings.

Convert the exported experiment with the companion benchmark's `from-experiment`
command, then pass its `trials.json` to `demo --trials`. Add
`--asset-config /path/to/local_assets.json --video --animation` to replay the
original UR5e + Robotiq 2F-85 USD and the configured object OBJ meshes.
See the benchmark's [local asset setup](https://github.com/Hanxin-Zhang/r2handoversim#local-ur5e--robotiq-and-object-meshes).
