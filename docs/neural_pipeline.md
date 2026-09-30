# Text2HOI → MANO → grasp selection → Isaac Sim

The neural path is now connected to grasp selection. Use the same object cloud
and scene at every step. The first release's procedural demos remain available
without any neural dependencies.

## 1. Install optional decoding dependencies

Inside your neural Python environment:

```bash
python -m pip install -e '.[text2hoi,mano,download]'
python -m pip install 'git+https://github.com/openai/CLIP.git'
python scripts/download_checkpoints.py
```

Obtain MANO separately under its original terms. `--mano-models` must point to
the directory containing `MANO_RIGHT.pkl` and/or `MANO_LEFT.pkl`. These are
trusted local model files; no model or decoded mesh is bundled here. Legacy
Chumpy-based files are supported on Python 3.11 through temporary compatibility
aliases during loading; global NumPy/inspect names are restored afterwards.
The optional MANO extra pins NumPy below 2 for legacy compatibility.

## 2. Generate an object and predict the receiving hand

```bash
intent-handover demo --object bottle
intent-handover text2hoi --checkpoints checkpoints/h2o \
  --point-cloud outputs/demo/bottle_points.npy \
  --prompt "Grasp a bottle with right hand." --hand right \
  --device cuda --frames 1 --seed 0 --output outputs/neural
```

## 3. Decode and select

```bash
intent-handover from-prediction \
  --scene outputs/demo/bottle_scene.json \
  --prediction outputs/neural/prediction.npz \
  --mano-models /path/to/mano/models \
  --frame 0 --mode FS --output outputs/predicted_hand
```

Outputs include `bottle_scene.json` with the predicted hand, `bottle_FS.json`
with ranked grasps and `bottle_FS.html` with a proxy visualization. The scene
contains MANO vertices/faces plus skeleton-based oriented boxes for collision
evaluation. Keep these generated assets out of a public repository unless their
redistribution terms permit it.

The bridge preserves Text2HOI's interleaved 6D rotation convention, converts to
MANO axis angles, decodes with zero shape coefficients and flat-hand mean, and
applies the inverse predicted object transform. Hand centre is the vertex mean;
direction is wrist-to-middle-fingertip. The palm normal comes from the
wrist/index/pinky-base triangle, with a left/right sign convention. Use
`--flip-palm-normal` if your input convention uses the opposite side of the palm.
Only the H2O checkpoint/object-transform convention is currently supported.

## 4. Replay in the separate benchmark

In the benchmark/Isaac Sim environment (adjust paths to the method outputs):

```bash
r2handoversim from-intent \
  --scene /path/to/intent-handover/outputs/predicted_hand/bottle_scene.json \
  --selection /path/to/intent-handover/outputs/predicted_hand/bottle_FS.json \
  --output outputs/neural_trial.json
r2handoversim demo --trial outputs/neural_trial.json --headless \
  --screenshot --animation --output outputs/neural_replay
```

The simulator renders the decoded mesh and evaluates box proxies around the
predicted skeleton by default. Add `--hand-collision mesh` to evaluate safety
against the static hand triangles in Isaac Sim; planning remains box-based. A one-frame coarse prediction on procedural geometry is a
working integration example, not a guarantee of realistic contact or the
paper's quality. The refiner and arbitrary-object grasp generation remain
outside this release.
