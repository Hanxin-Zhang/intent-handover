"""Intent-aware candidate filtering and avoidance-cost ranking."""
import numpy as np
from .geometry import contains, projected_width, transform, unit, vector

MODES = {"FS": (True, True), "A1": (False, True),
         "A2": (True, False), "A3": (False, False)}


def select_grasp(scene, mode="FS"):
    """No learned models or hardware required. All geometry is in object frame.

    Usage constraint checks the candidate's object-surface approach intersection.
    In A2/A3 the first valid candidate is selected deterministically; this tie
    policy is a release implementation choice, not recovered experiment code.
    """
    if scene.get("schema_version") != "handover.scene.v1" or scene.get("units") != "m":
        raise ValueError("Expected handover.scene.v1 with units=m")
    if mode not in MODES:
        raise ValueError("Mode must be FS, A1, A2 or A3")
    use_region, use_avoidance = MODES[mode]
    if scene["intent"].get("needs_clarification", False):
        raise ValueError("Intent is ambiguous; resolve it before selecting a grasp")
    if scene["intent"]["object_id"] != scene["object"]["id"]:
        raise ValueError("Intent and scene object ids differ")
    max_width = float(scene["gripper"]["max_opening_m"])
    if not np.isfinite(max_width) or max_width <= 0:
        raise ValueError("Maximum gripper opening must be positive")
    hand = scene["receiving_hand"]
    direction, center = unit(hand["direction"]), vector(hand["center"])
    regions = scene["object"]["usage_regions"]
    intended = scene["intent"]["human_region"]
    if intended not in regions:
        raise ValueError(f"Unknown human region: {intended}")
    rows, seen = [], set()
    for candidate in scene["candidates"]:
        cid = candidate["id"]
        if cid in seen:
            raise ValueError(f"Duplicate candidate id: {cid}")
        seen.add(cid)
        t = transform(candidate["T_object_gripper"])
        hit = vector(candidate["approach_point_object"])
        # Width of the provided object proxy along gripper closing direction.
        width = projected_width(scene["object"]["boxes"], t[:3, 1])
        in_usage = any(contains(b, hit) for b in regions[intended])
        on_object = any(contains(b, hit) for b in scene["object"]["boxes"])
        distance = float(np.linalg.norm(t[:3, 3] - center))
        cosine = float(unit(t[:3, 2]) @ direction)
        cost = cosine - distance
        rejected = []
        if not on_object:
            rejected.append("approach_point_outside_object")
        if width > max_width + 1e-9:
            rejected.append("width_exceeds_aperture")
        if use_region and in_usage:
            rejected.append("human_usage_region")
        rows.append({"id": cid, "T_object_gripper": t.tolist(),
                     "approach_point_object": hit.tolist(), "width_m": width,
                     "cosine": cosine, "distance_m": distance, "avoidance_cost": cost,
                     "in_human_region": in_usage, "valid": not rejected,
                     "rejection_reasons": rejected})
    valid = [r for r in rows if r["valid"]]
    best = min(valid, key=lambda r: r["avoidance_cost"]) if use_avoidance and valid else (valid[0] if valid else None)
    return {"schema_version": "handover.selection.v1", "units": "m",
            "object_id": scene["object"]["id"], "mode": mode,
            "status": "ok" if best else "no_feasible_grasp", "selected": best,
            "candidates": rows, "provenance": scene.get("provenance", "user input")}
