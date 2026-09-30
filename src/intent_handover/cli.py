import argparse
import json
from pathlib import Path
from .core import MODES
from .demos import NAMES, load_scene


def main(argv=None):
    parser = argparse.ArgumentParser(description="Intent-Handover runnable method demos")
    sub = parser.add_subparsers(dest="command", required=True)
    weights = sub.add_parser("download-weights", help="Download or verify original Text2HOI weights with SHA-256")
    weights.add_argument("--output", type=Path, default=Path("checkpoints/h2o"))
    weights.add_argument("--force", action="store_true")
    weights.add_argument("--verify-only", action="store_true")
    ablation = sub.add_parser("ablate", help="Run FS/A1/A2/A3 and export a paired experiment")
    sources = ablation.add_mutually_exclusive_group()
    sources.add_argument("--scene", type=Path)
    sources.add_argument("--manifest", type=Path)
    sources.add_argument("--object", choices=[*NAMES, "all"], default="all")
    ablation.add_argument("--output", type=Path, default=Path("outputs/ablation"))
    pipeline = sub.add_parser("pipeline", help="Run scene -> Text2HOI -> MANO -> grasp selection")
    source = pipeline.add_mutually_exclusive_group(required=True)
    source.add_argument("--scene", type=Path)
    source.add_argument("--object", choices=NAMES)
    pipeline.add_argument("--intent", type=Path, help="Structured intent JSON returned by your model")
    pipeline.add_argument("--checkpoints", type=Path, required=True)
    pipeline.add_argument("--mano-models", type=Path, required=True)
    pipeline.add_argument("--skeleton", type=Path)
    pipeline.add_argument("--device", default="cuda")
    pipeline.add_argument("--seed", type=int, default=0)
    pipeline.add_argument("--output", type=Path, default=Path("outputs/pipeline"))
    dataset = sub.add_parser("dataset", help="Import original local objects from a Text2HOI han config")
    dataset.add_argument("--config", type=Path, required=True)
    dataset.add_argument("--project-root", type=Path)
    dataset.add_argument("--object", default="all")
    dataset.add_argument("--scale-to-m", type=float, default=1.)
    dataset.add_argument("--output", type=Path, default=Path("outputs/dataset"))
    demo = sub.add_parser("demo", help="Run bundled CPU examples")
    demo.add_argument("--object", choices=[*NAMES, "all"], default="all")
    demo.add_argument("--mode", choices=MODES, default="FS")
    demo.add_argument("--output", type=Path, default=Path("outputs/demo"))
    run = sub.add_parser("select", help="Select from a handover.scene.v1 JSON")
    run.add_argument("scene", type=Path)
    run.add_argument("--intent", type=Path, help="Apply a validated structured intent to this scene")
    run.add_argument("--mode", choices=MODES, default="FS")
    run.add_argument("--output", type=Path, default=Path("outputs/custom"))
    prompt = sub.add_parser("prompt", help="Print the authored system/user prompts for a VLM or LLM")
    prompt.add_argument("--instruction", required=True)
    catalog_source = prompt.add_mutually_exclusive_group()
    catalog_source.add_argument("--scene", type=Path, action="append")
    catalog_source.add_argument("--manifest", type=Path)
    delivery = sub.add_parser("delivery", help="Compute paper Sec. III-B delivery target from skeletal keypoints")
    delivery.add_argument("--scene", type=Path, required=True)
    delivery.add_argument("--selection", type=Path, required=True)
    delivery.add_argument("--skeleton", type=Path, required=True)
    delivery.add_argument("--output", type=Path, default=Path("outputs/delivery.json"))
    bridge = sub.add_parser("from-prediction", help="Decode a neural hand with local MANO, then select a grasp")
    bridge.add_argument("--scene", type=Path, required=True)
    bridge.add_argument("--prediction", type=Path, required=True)
    bridge.add_argument("--mano-models", type=Path, required=True)
    bridge.add_argument("--frame", type=int, default=0)
    bridge.add_argument("--flip-palm-normal", action="store_true")
    bridge.add_argument("--mode", choices=MODES, default="FS")
    bridge.add_argument("--output", type=Path, default=Path("outputs/predicted_hand"))
    neural = sub.add_parser("text2hoi", help="Optional coarse prediction using original Text2HOI weights")
    neural.add_argument("--checkpoints", type=Path, required=True)
    neural.add_argument("--point-cloud", type=Path, required=True, help="N x 3 point cloud in metres (.npy)")
    neural.add_argument("--prompt", required=True)
    neural.add_argument("--hand", choices=["left", "right"], default="right")
    neural.add_argument("--device", default="cuda")
    neural.add_argument("--seed", type=int, default=0)
    neural.add_argument("--frames", type=int, default=1)
    neural.add_argument("--output", type=Path, default=Path("outputs/text2hoi"))
    args = parser.parse_args(argv)
    try:
        if args.command == "download-weights":
            from .weights import download_weights, verify_weights
            weights = verify_weights(args.output) if args.verify_only else download_weights(args.output, args.force)
            print(f"Verified {len(weights)} checkpoints: {args.output.resolve()}")
            return
        if args.command == "ablate":
            from .workflows import ablate, manifest_scenes
            scenes = (manifest_scenes(args.manifest) if args.manifest else [json.loads(args.scene.read_text())]
                      if args.scene else [load_scene(n) for n in (NAMES if args.object == "all" else [args.object])])
            result = ablate(scenes, args.output)
            print(f"{len(result['objects'])} objects × 4 modes: {(args.output/'experiment.json').resolve()}")
            return
        if args.command == "pipeline":
            from .workflows import run_pipeline
            scene = json.loads(args.scene.read_text()) if args.scene else load_scene(args.object)
            state = run_pipeline(scene, args.checkpoints, args.mano_models, args.output, args.device, args.seed,
                json.loads(args.intent.read_text()) if args.intent else None,
                json.loads(args.skeleton.read_text()) if args.skeleton else None)
            print(f"Pipeline {state['selection_status']}: {(args.output/'pipeline.json').resolve()}")
            if state['selection_status'] != 'ok': parser.exit(2, "Prediction completed but no feasible grasp was found\n")
            return
        if args.command == "dataset":
            from .dataset import import_dataset
            manifest = import_dataset(args.config, args.output, args.project_root, args.object, args.scale_to_m)
            print(f"Imported {len(manifest['objects'])} objects; {len(manifest['missing'])} missing cached assets. Manifest: {(args.output/'dataset.json').resolve()}")
            return
        if args.command == "delivery":
            from .execution import delivery_target
            result = delivery_target(json.loads(args.scene.read_text()), json.loads(args.selection.read_text()),
                                     json.loads(args.skeleton.read_text()))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2, allow_nan=False))
            print(args.output.resolve())
            return
        if args.command == "prompt":
            from importlib.resources import files
            from .workflows import manifest_scenes
            scenes = (manifest_scenes(args.manifest) if args.manifest else [json.loads(p.read_text()) for p in args.scene]
                      if args.scene else [load_scene(n) for n in NAMES])
            catalog = [{"object_id": s["object"]["id"], "regions": list(s["object"]["usage_regions"])} for s in scenes]
            print(json.dumps({"system": files(__package__).joinpath("assets", "intent_system.txt").read_text(),
                              "user": {"scene_catalog": catalog, "instruction": args.instruction}}, indent=2, ensure_ascii=False))
            return
        if args.command == "text2hoi":
            from .text2hoi import predict
            predict(args)
            return
        if args.command == "from-prediction":
            from .prediction_bridge import decode_prediction
            scenes = [decode_prediction(json.loads(args.scene.read_text()), args.prediction,
                       args.mano_models, args.frame, args.flip_palm_normal)]
        else:
            scenes = ([load_scene(n) for n in (NAMES if args.object == "all" else [args.object])]
                  if args.command == "demo" else [json.loads(args.scene.read_text())])
        args.output.mkdir(parents=True, exist_ok=True)
        for scene in scenes:
            from .workflows import apply_intent, export_selection
            if args.command == "select" and args.intent:
                scene = apply_intent(scene, json.loads(args.intent.read_text()))
            result, files = export_selection(scene, args.output, args.mode)
            selected = result["selected"]
            print(f"{scene['object']['id']}: {selected['id'] if selected else result['status']} -> {(args.output/files['report']).resolve()}")
    except (ValueError, KeyError, OSError, ImportError, RuntimeError) as exc:
        parser.exit(2, f"Error: {exc}\n")
