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

Exports replace completion indexes with `handover.incomplete.v1` while running
and on failure. The complete `dataset.json`, `experiment.json`, `replay.json`
or selection schema is published only after its referenced outputs have been
written. Rerun the command to recover; do not run multiple writers in one output
directory. `select`, `demo`, and `from-prediction` return exit code 2 if any
requested scene has no feasible grasp; the rejection report is still saved.

## Verify replay preserves the method

Benchmark 0.8.0 saves the **resolved** `*_trial.json` after asset fitting and
retargeting. Use that file, rather than the pre-adaptation input, to check the
actual replay configuration:

```bash
intent-handover audit-replay \
  --scene outputs/demo/hammer_scene.json \
  --selection outputs/demo/hammer_FS.json \
  --trial /path/to/r2handoversim/outputs/replay/hammer_intent_aware_trial.json \
  --output outputs/hammer_replay_audit.json
```

Add `--delivery outputs/ergonomic_delivery.json` to require the original
world-frame delivery target as well. Exit code 0 means the checked grasp,
proxy annotations and receiver reference point agree; it is not a trajectory,
collision, holding-force or paper-success certificate. Exit code 2 records the
differences. The audit recomputes selection to catch stale method outputs.

This adapter implements the documented benchmark 0.7/0.8 width behavior:
global projection, or `asset_contact_fit.width_m` for bilateral asset fits.
Current benchmark versions do not propagate `local_pad_proxy`; the audit
therefore rejects replay of newly imported local-width scenes even if one
width happens to coincide numerically. Original asset-tool calibration and
post-fit method reselection are also not certified. The bundled global-width
proxy demo workflow remains compatible. Future benchmark policies need an
explicit audit adapter update; merely adding an unused width field is not
sufficient. See [integration requirements](geometry_audit.md).

## Neural prediction through simulation

See [the complete setup and one-command recipe](neural_pipeline.md) for original
Text2HOI weights, MANO decoding, optional skeletal delivery and Isaac Sim replay.
