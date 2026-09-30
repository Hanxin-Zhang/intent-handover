"""Read-only checks of the documented R2HandoverSim 0.7/0.8 trial contract.

No simulator dependency, retargeting, grasp repair or physics certification.
Use the resolved *_trial.json exported by the simulator for post-run checks.
"""
import numpy as np
from .core import select_grasp
from .geometry import inverse, points, projected_width, transform


def audit_replay(scene, selection, trial, delivery=None):
    if selection.get("schema_version") != "handover.selection.v1" or selection.get("units") != "m":
        raise ValueError("Expected handover.selection.v1 with units=m")
    if trial.get("schema_version") != "handover.trial.v1" or trial.get("units") != "m":
        raise ValueError("Expected handover.trial.v1 with units=m")
    current = select_grasp(scene, selection["mode"])
    expected = current["selected"]
    saved = selection.get("selected")
    if not expected or selection.get("status") != "ok" or not saved:
        raise ValueError("Replay audit requires a feasible method selection")
    issues = []
    def check(condition, reason):
        if not condition:
            issues.append(reason)
    def close(a, b):
        a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        return a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all() and np.allclose(a, b, atol=1e-8, rtol=0)
    check(selection["object_id"] == scene["object"]["id"] == trial.get("object_id"), "object_id_changed")
    check(saved["id"] == expected["id"] and close(saved["T_object_gripper"], expected["T_object_gripper"])
          and close(saved["width_m"], expected["width_m"]), "selection_stale_or_modified")
    actual_pose = transform(trial["T_object_gripper"])
    check(close(actual_pose, expected["T_object_gripper"]), "grasp_pose_changed")
    check(close(trial["max_opening_m"], scene["gripper"]["max_opening_m"]), "maximum_aperture_changed")
    # These are the two width policies actually implemented by benchmark 0.8.
    fit = trial.get("asset_contact_fit", {})
    if fit.get("status") == "bilateral_surface_fit":
        actual_width = float(fit["width_m"])
        width_source = "asset_contact_fit"
    else:
        actual_width = projected_width(trial["object_boxes"], actual_pose[:3, 1])
        width_source = "global_projection"
    check(np.isfinite(actual_width) and actual_width > 0 and close(actual_width, expected["width_m"]), "replay_width_changed")
    if current["grasp_contract"]["width_policy"] != width_source:
        issues.append("width_policy_not_preserved")
    if "asset_robot" in trial or "T_tcp_asset_tool" in trial:
        issues.append("asset_tool_frame_requires_explicit_method_calibration")
    # Exact copied box annotations are part of this adapter contract. Compare
    # numeric geometry rather than optional labels or JSON formatting.
    def boxes_equal(left, right):
        if len(left) != len(right): return False
        return all(close(a["center"], b["center"]) and close(a["half_extents"], b["half_extents"])
                   and close(a.get("rotation", np.eye(3)), b.get("rotation", np.eye(3)))
                   for a, b in zip(left, right))
    check(boxes_equal(scene["object"]["boxes"], trial["object_boxes"]), "object_proxy_changed")
    region = scene["object"]["usage_regions"][scene["intent"]["human_region"]]
    check(boxes_equal(region, trial["usage_boxes"]), "usage_region_changed")
    world_object = transform(trial["target_T_world_gripper"]) @ inverse(actual_pose)
    check(close(points(inverse(world_object), trial["palm_position_world"]), scene["receiving_hand"]["center"]),
          "receiver_object_relation_changed")
    if trial.get("experiment", {}).get("paired_receiver_preserved") is False:
        issues.append("paired_receiver_not_preserved")
    if delivery is not None:
        if delivery.get("schema_version") != "handover.delivery.v1" or delivery.get("units") != "m":
            raise ValueError("Expected handover.delivery.v1 with units=m")
        check(delivery["object_id"] == current["object_id"] and delivery["grasp_id"] == expected["id"],
              "delivery_identity_changed")
        check(close(world_object, delivery["T_world_object"]) and
              close(trial["target_T_world_gripper"], delivery["T_world_gripper"]), "delivery_target_changed")
    return {"schema_version": "handover.replay_audit.v1", "units": "m",
            "status": "equivalent" if not issues else "not_equivalent",
            "scope": "Grasp, proxy annotations and receiver reference point only; not trajectory or physics validation",
            "object_id": current["object_id"], "mode": current["mode"], "issues": issues,
            "expected_width_m": expected["width_m"], "replay_width_m": actual_width,
            "expected_width_source": current["grasp_contract"]["width_policy"], "replay_width_source": width_source,
            "delivery_checked": delivery is not None, "physical_grasp_verified": False}
