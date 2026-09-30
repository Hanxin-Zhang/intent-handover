# Import the original local dataset

`Text2HOI/configs/config.yaml` selects `dataset: han`; the dataset YAML specifies:

```yaml
name: han
root: data/han
obj_root: data/han/object
data_obj_pc_path: data/han/obj.pkl
```

The importer resolves these paths relative to the original project root, not
your current working directory. It accepts either the main config or
`configs/dataset/han.yaml`. For configurations moved outside a `configs/` tree,
pass `--project-root /path/to/Text2HOI` explicitly. The original local pickle is
loaded like the project's `ObjectModel`; only use your trusted dataset cache.

## Available data verified on 2026-09-30

16 PLY files exist: binoculars, bottle, bowl, can, cup, dispenser, drill,
eyeglasses, gamecontroller, hammers, headphones, knife, pincer, scissors,
screwdriver and toothbrush. Names, including `hammers`, are retained verbatim.
Every PLY has 8192 vertices and **zero faces**: these are point clouds, not
triangle meshes. The cache contains 1024 points per object. Coordinates are used
in metres, consistent with the original han loader, without recentering or
rescaling. Use explicit `--scale-to-m` only for a differently scaled input.

The cache also lists `eyeglasses4`, but its PLY is missing. It is reported in
`dataset.json`, not silently substituted with `eyeglasses`. Source hashes and
bounds are recorded in [the inventory](dataset_inventory.json). H2O/GRAB/ARCTIC
YAML files also exist, but their configured object roots are absent in this
checkout. This adapter does not infer alternate dataset frame conventions.

## Import and view

```bash
python -m pip install -e '.[dataset]'
intent-handover dataset --config /path/to/Text2HOI/configs/config.yaml \
  --output outputs/han_dataset
```

For each available object the command writes:

- `*_points.npy`: cached 1024-point input for Text2HOI, preserving coordinates.
- `*_surface.npy`: complete original PLY point cloud.
- `*_scene.json`: source cloud, collision proxies and explicitly generated demo annotations.
- `*_FS.json` / `*_FS.html`: grasp-selection result and source-point-cloud view.
- `dataset.json`: config/cache/asset hashes, bounds, paths and missing entries.

The importer does not modify the source data or fix the stale pickle in place.
It retains each available file and records the missing one. Raw/derived data
goes under ignored `outputs/`; the repository distributes the loader, not the
third-party dataset. No download credentials or developer path is baked into
the runtime.

## What is original and what is generated

The source object clouds and cached neural inputs are original local data.
The config/cache does **not** provide the paper's robot grasp annotations,
functional-region masks, trial sequences or S0/S1 assignments. To make all
available objects runnable, this release adds a clearly labelled geometry-only
bootstrap: 30 axis-based grasp proposals, a hand proxy outside the long-axis
end, and a receiving zone covering the lower 35% of that axis. These are not
Multi-GraspLLM proposals or recovered semantic labels.

Collision geometry is a union of boxes fitted to occupied cells in a 3x3x3
grid of the original point cloud. Selection uses ray/box surface intersections
and the paper's width/avoidance score. The full source cloud is used for display.
`evaluation_split=S0` is an explicit **demo setting**, so functional-region
quality is not counted as a benchmark success claim. Users with real labels can
replace `usage_regions`, candidates and split in the scene contract. Changing
S0 to S1 alone does not turn generated labels into paper ground truth.

## Use actual data with the original neural weights

The main config's example mentions binoculars. A verified left-hand example:

```bash
intent-handover text2hoi --checkpoints checkpoints/h2o \
  --point-cloud outputs/han_dataset/binoculars_points.npy \
  --prompt "Grasp binoculars with left hand." --hand left \
  --device cuda --frames 1 --seed 0 --output outputs/han_neural
intent-handover from-prediction \
  --scene outputs/han_dataset/binoculars_scene.json \
  --prediction outputs/han_neural/prediction.npz \
  --mano-models /path/to/mano/models --output outputs/han_predicted
```

See [neural setup](neural_pipeline.md) for optional dependencies/weights. This
uses original H2O Text2HOI weights on a local han object, not a retrained model.
The generated hand replaces the proxy; object points remain in their original
frame. Prediction quality is not implied by a completed run.
