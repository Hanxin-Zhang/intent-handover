import argparse
import json
from pathlib import Path
from .core import MODES, select_grasp
from .demos import NAMES, load_scene, sample_surface
from .report import write_report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Intent-Handover runnable method demos")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run bundled CPU examples")
    demo.add_argument("--object", choices=[*NAMES, "all"], default="all")
    demo.add_argument("--mode", choices=MODES, default="FS")
    demo.add_argument("--output", type=Path, default=Path("outputs/demo"))
    run = sub.add_parser("select", help="Select from a handover.scene.v1 JSON")
    run.add_argument("scene", type=Path)
    run.add_argument("--mode", choices=MODES, default="FS")
    run.add_argument("--output", type=Path, default=Path("outputs/custom"))
    prompt = sub.add_parser("prompt", help="Print the authored system/user prompts for a VLM or LLM")
    prompt.add_argument("--instruction", required=True)
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
            catalog = [{"object_id": n, "regions": list(load_scene(n)["object"]["usage_regions"])} for n in NAMES]
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
            result = select_grasp(scene, args.mode)
            # Object ids are metadata, never untrusted filesystem paths.
            import re
            name = re.sub(r"[^a-zA-Z0-9_-]", "_", str(scene["object"]["id"]))
            stem = args.output / f"{name}_{args.mode}"
            stem.with_suffix(".json").write_text(json.dumps(result, indent=2, allow_nan=False))
            (args.output / f"{name}_scene.json").write_text(json.dumps(scene, indent=2, allow_nan=False))
            import numpy as np
            np.save(args.output / f"{name}_points.npy", sample_surface(scene), allow_pickle=False)
            write_report(scene, result, stem.with_suffix(".html"))
            selected = result["selected"]
            print(f"{name}: {selected['id'] if selected else result['status']} -> {stem.with_suffix('.html').resolve()}")
    except (ValueError, KeyError, OSError, ImportError) as exc:
        parser.exit(2, f"Error: {exc}\n")
