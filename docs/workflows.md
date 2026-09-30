# Runnable workflows

## Structured intent

Generate a prompt containing the actual object/region catalog:

```bash
intent-handover demo --object hammer
intent-handover prompt --scene outputs/demo/hammer_scene.json \
  --instruction "I need to hammer a nail." > outputs/prompt.json
```

Send the `system` and `user` fields to your chosen model and save its JSON reply.
The repository supplies the prompt; no paid service or API key is required for
the bundled examples. Try the included response directly:

```bash
intent-handover select outputs/demo/hammer_scene.json \
  --intent examples/hammer_intent.json --output outputs/intent
```

`select --intent` and `pipeline --intent` validate the object, region names,
hand side, short Text2HOI prompt and `needs_clarification=false`. Ambiguous
responses are rejected. Selection uses the specified human region as its
exclusion region; `robot_region` records the requested counterpart but is not
an additional hard inclusion constraint. Changing a prompt with `select` alone
does not generate a new hand; use `pipeline` for neural prediction.

For local datasets, use `prompt --manifest outputs/han_dataset/dataset.json`.
Imported regions are generated demo labels, not recovered functional labels.

## Four method ablations

```bash
intent-handover ablate --output outputs/ablation
# Or use every object imported from the original dataset config:
intent-handover ablate --manifest outputs/han_dataset/dataset.json \
  --output outputs/han_ablation
```

This executes FS/A1/A2/A3 on the same input scene for each object, writes an
HTML and selection JSON per mode, and exports `ablation.csv` plus
`experiment.json`. `--scene` can supply one custom or predicted-hand scene.

In the separately installed benchmark, with its `[planning]` extra:

```bash
r2handoversim from-experiment \
  --manifest /path/to/intent-handover/outputs/ablation/experiment.json \
  --seed 0 --output outputs/ablation_trials
r2handoversim demo --trials outputs/ablation_trials/trials.json --headless \
  --screenshot --render-every 6 --output outputs/ablation_isaac
```

The converter holds the world-frame hand and object target fixed within each
object across modes, then plans each selected grasp separately. Results include
planning failures. `conversion.json` separately lists any modes without a
feasible grasp; those have no replay and are not included in simulator metric
denominators. Read that file together with the simulator report.

These are executable method ablations, separate from the benchmark's authored
offline variants and the paper's four baseline systems.

## Neural prediction through simulation

See [the complete setup and one-command recipe](neural_pipeline.md) for original
Text2HOI weights, MANO decoding, optional skeletal delivery and Isaac Sim replay.
