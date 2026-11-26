#!/usr/bin/env python3
"""Create and optionally write draft cuboids to the local CVAT task.

This is a geometry-based proposal tool, not a trained detector. It clusters
foreground returns in BEV and estimates an oriented box. Class and heading are
ambiguous in a single LiDAR scan, so every proposal is explicitly marked for
human review. Writes are opt-in with --apply and never replace annotations.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import uuid
import zipfile
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cvat_lab"))
sys.path.insert(0, str(ROOT / "scripts"))
import vf_common as vf  # noqa: E402


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    at = q * (len(values) - 1)
    lo = int(at)
    hi = min(lo + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (at - lo)


def proposals(points, radius: float, min_cells: int, max_boxes: int = 6) -> list[dict]:
    """Connected components over occupied BEV cells, followed by PCA boxes."""
    cell = defaultdict(list)
    for i in range(len(points) // 4):
        x, y, z = points[4*i:4*i+3]
        if not all(math.isfinite(v) for v in (x, y, z)):
            continue
        if math.hypot(x, y) > 50 or z < -1.35 or z > 4.5:
            continue
        cell[(math.floor(x / radius), math.floor(y / radius))].append((x, y, z))

    seen, components = set(), []
    reach = 1
    for start in cell:
        if start in seen:
            continue
        seen.add(start)
        queue, cells = deque([start]), []
        while queue:
            key = queue.popleft()
            cells.append(key)
            for dx in range(-reach, reach + 1):
                for dy in range(-reach, reach + 1):
                    nxt = (key[0] + dx, key[1] + dy)
                    if nxt not in seen and nxt in cell:
                        seen.add(nxt)
                        queue.append(nxt)
        if len(cells) >= min_cells:
            pts = [p for k in cells for p in cell[k]]
            if len(pts) >= 12:
                components.append(pts)

    out = []
    for pts in components:
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        xx = sum((p[0]-mx)**2 for p in pts) / len(pts)
        yy = sum((p[1]-my)**2 for p in pts) / len(pts)
        xy = sum((p[0]-mx)*(p[1]-my) for p in pts) / len(pts)
        yaw = 0.5 * math.atan2(2*xy, xx-yy)
        c, s = math.cos(yaw), math.sin(yaw)
        along = [c*p[0] + s*p[1] for p in pts]
        across = [-s*p[0] + c*p[1] for p in pts]
        zvals = [p[2] for p in pts]
        a0, a1 = percentile(along, .03), percentile(along, .97)
        b0, b1 = percentile(across, .03), percentile(across, .97)
        # VF road is near z=-1.7 m. The scan sees object surfaces, not a full
        # bottom plane, so anchor the draft footprint to that approximate road.
        z0, z1 = -1.7, percentile(zvals, .97)
        length, width, height = a1-a0, b1-b0, z1-z0
        if length < width:
            length, width = width, length
            yaw += math.pi / 2
        if not (0.35 <= width <= 4.5 and 0.45 <= length <= 18 and 0.45 <= height <= 5):
            continue
        # Convert PCA-coordinate centre to the VF frame.
        center_a, center_b = (a0+a1)/2, (b0+b1)/2
        cx = c*center_a - s*center_b
        cy = s*center_a + c*center_b
        # Conservative class hint. Always human-review due to overlap in sizes.
        if height < 2.2 and length < 3.2:
            label, confidence = "Pedestrian", "low"
        elif height < 2.2 and length < 4.0:
            label, confidence = "Cyclist", "low"
        elif height >= 2.75 and length >= 7.0:
            label, confidence = "Bus", "low"
        elif length >= 5.2 or height >= 2.5:
            label, confidence = "Truck", "low"
        else:
            label, confidence = "Car", "low"
        # The project's CVAT convention expects the red +X mark to face the
        # opposite direction from the PCA axis chosen above.
        yaw += math.pi
        out.append({"x": round(cx, 3), "y": round(cy, 3), "z": round((z0+z1)/2, 3),
                    "length": round(length, 3), "width": round(width, 3), "height": round(height, 3),
                    "yaw_rad": round(vf.wrap_yaw(yaw), 4), "label_suggestion": label,
                    "confidence": confidence, "points": len(pts), "needs_review": True,
                    "review_notes": "Verify class, heading, footprint, ground contact, and 15-20% visibility rule."})
    return sorted(out, key=lambda b: math.hypot(b["x"], b["y"]))[:max_boxes]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--student", default=None, help="ID from configs/lab.ini; defaults to configured ID")
    ap.add_argument("--data", type=Path, default=None, help="VF data directory; defaults to configs/lab.ini")
    ap.add_argument("--task-id", type=int, help="CVAT task ID; defaults to task D13-<student>")
    ap.add_argument("--apply", action="store_true", help="write draft boxes to unannotated frames in local CVAT")
    ap.add_argument("--cell-size", type=float, default=.35, help="BEV clustering cell size in metres")
    ap.add_argument("--min-cells", type=int, default=4, help="minimum occupied cells per proposal")
    ap.add_argument("--per-frame", type=int, default=6, help="nearest proposals to keep per frame: 5 or 6 (default: 6)")
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "auto-label-proposals.json")
    args = ap.parse_args()
    if args.cell_size <= 0 or args.min_cells < 1 or args.per_frame not in (5, 6):
        ap.error("--cell-size and --min-cells must be positive; --per-frame must be 5 or 6")
    from lab import data_dir, load_config  # noqa: PLC0415
    cfg = load_config()
    student = vf.normalize_student(args.student or cfg["student"])
    data = args.data or data_dir(cfg)
    seqs = vf.list_sequences(data)
    frames = vf.select_frames(student, {seq: len(stamps) for seq, stamps in seqs.items()})
    result = {"format": "vf-cuboid-proposals-v1", "method": "BEV connected components + PCA",
              "warning": "Draft suggestions only. Geometry cannot reliably infer class/heading; review every box in CVAT.",
              "student": student, "coordinate_system": "VF: x left, y back, z up; metres",
              "frames": []}
    for name in frames:
        seq, index = vf.parse_frame_name(name)
        path = data / f"sequence_{seq:02d}" / "lidar" / f"{seqs[seq][index]}.bin"
        boxes = proposals(vf.read_bin(path), args.cell_size, args.min_cells, args.per_frame)
        result["frames"].append({"frame": name, "boxes": boxes})
        print(f"{name}: {len(boxes)} proposals")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Saved review proposals: {args.out}")
    if args.apply:
        apply_to_cvat(cfg, student, result["frames"], args.task_id, data, seqs)
    else:
        print("Preview only: rerun with --apply to add drafts to CVAT (existing annotations are preserved).")
    return 0


def apply_to_cvat(cfg: dict, student: str, frame_rows: list[dict], task_id: int | None,
                  data: Path, seqs: dict[int, list[str]]) -> None:
    """Import 3D cuboids through CVAT's point-cloud annotation importer."""
    import getpass
    import os
    from urllib.parse import urlparse

    host = cfg["cvat_host"]
    if urlparse(host).hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise SystemExit(f"Chỉ ghi vào CVAT local; host hiện tại là {host!r}.")
    try:
        from cvat_sdk import make_client
        from cvat_sdk.api_client.exceptions import ApiException
        from cvat_sdk.core.exceptions import BackgroundRequestException
    except ImportError as exc:
        raise SystemExit("Thiếu cvat-sdk. Kích hoạt .venv và cài `pip install -r requirements.txt`.") from exc

    user = cfg.get("cvat_user", "").strip()
    if not user:
        raise SystemExit("Chưa điền cvat_user trong configs/lab.ini.")
    password = os.environ.get("CVAT_PASSWORD") or getpass.getpass(f"Mật khẩu CVAT cho {user}: ")
    client = make_client(host, credentials=(user, password))
    if cfg.get("cvat_org"):
        client.organization_slug = cfg["cvat_org"]
    name = vf.task_name(student)
    matches = [t for t in client.tasks.list() if (task_id is not None and t.id == task_id) or
               (task_id is None and t.name == name)]
    if len(matches) != 1:
        raise SystemExit(f"Cần đúng một task CVAT; tìm thấy {len(matches)} cho {task_id or name}.")
    task = matches[0]
    expected = [row["frame"] for row in frame_rows]
    frame_names = [f.name for f in task.get_meta().frames]
    actual = [Path(n).stem.replace("_pcd", "") for n in frame_names]
    if actual != expected:
        raise SystemExit(f"Task {task.name} không khớp 10 frame được giao; không ghi nhãn.")
    if not task.get_jobs():
        raise SystemExit(f"Task {task.name} chưa có job; không ghi nhãn.")

    labels = {label.name for label in task.get_labels()}
    required = set(vf.CLASS_IDS)
    if not required.issubset(labels):
        raise SystemExit(f"Task thiếu nhãn: {', '.join(sorted(required - labels))}.")
    annotations = task.get_annotations()
    if annotations.tracks:
        raise SystemExit("Task đang có annotation dạng Track; dừng để tránh chồng cuboid nháp lên nhãn track.")
    occupied = {shape.frame for shape in annotations.shapes}
    by_index = {name: i for i, name in enumerate(actual)}
    existing_count = len(annotations.shapes)
    if existing_count > 70:
        raise SystemExit(f"Task đã có {existing_count} Shape cuboid, vượt mục tiêu 60–70; tool không xóa annotation hiện có.")
    if existing_count >= 60:
        print(f"Task đã có {existing_count} Shape cuboid (mục tiêu 60–70); không cần thêm.")
        return

    import_frames = []
    skipped = []
    selected_count = existing_count
    for frame in frame_rows:
        index = by_index[frame["frame"]]
        if index in occupied:
            skipped.append(frame["frame"])
            continue
        if frame["boxes"]:
            boxes = frame["boxes"][:min(6, 70 - selected_count)]
            if boxes:
                import_frames.append(({**frame, "boxes": boxes}, index))
                selected_count += len(boxes)
            if selected_count >= 60 or selected_count >= 70:
                break
    total = sum(len(frame["boxes"]) for frame, _ in import_frames)
    print(f"Task: {task.name} (#{task.id}) | đã có {existing_count}, thêm tối đa {total}, mục tiêu 60–70 | bỏ qua frame đã có cuboid: {', '.join(skipped) or 'không'}")
    if not total:
        print(f"Không có hộp nào để thêm; task hiện có {existing_count} Shape cuboid.")
        if existing_count < 60:
            print("Chưa đạt 60 cuboid: các frame còn lại đã có Shape hoặc không còn proposal phù hợp.")
        return
    out_zip = ROOT / "work" / f"auto-label-{task.id}-sly-import.zip"
    write_sly_archive(out_zip, import_frames, data, seqs)
    before_count = len(annotations.shapes) + len(annotations.tracks)
    try:
        task.import_annotations("Sly Point Cloud Format 1.0", out_zip, import_mode="append")
    except (ApiException, BackgroundRequestException) as exc:
        body = getattr(exc, "body", None)
        body = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body or exc)
        raise SystemExit(f"CVAT từ chối nhập annotations 3D: {body}") from None
    after = task.get_annotations()
    after_count = len(after.shapes) + len(after.tracks)
    print(f"Task #{task.id}: số annotation {before_count} -> {after_count}.")
    print(f"Đã gửi {total} cuboid nháp qua Sly Point Cloud Format. Mở CVAT để kiểm và chỉnh rồi Save.")


def write_sly_archive(out_zip: Path, frames: list[tuple[dict, int]], data: Path,
                      seqs: dict[int, list[str]]) -> None:
    """Build the SLY point-cloud format CVAT uses for native 3D annotations."""
    import_frames = []
    key_ids = {"tags": {}, "objects": {}, "figures": {}, "videos": {}}
    next_id = 1
    for frame, frame_index in frames:
        frame_key = uuid.uuid4().hex
        key_ids["videos"][frame_key] = frame_index
        seq, index = vf.parse_frame_name(frame["frame"])
        objects, figures = [], []
        for box in frame["boxes"]:
            object_key, figure_key = uuid.uuid4().hex, uuid.uuid4().hex
            objects.append({"key": object_key, "classTitle": box["label_suggestion"], "tags": []})
            figures.append({
                "key": figure_key, "objectKey": object_key, "geometryType": "cuboid_3d",
                "geometry": {
                    "position": {"x": box["x"], "y": box["y"], "z": box["z"]},
                    "rotation": {"x": 0, "y": 0, "z": box["yaw_rad"]},
                    "dimensions": {"x": box["length"], "y": box["width"], "z": box["height"]},
                },
            })
            key_ids["objects"][object_key] = next_id
            key_ids["figures"][figure_key] = next_id
            next_id += 1
        import_frames.append((frame, frame_key, objects, figures))

    meta = {"classes": [{"id": n, "title": name, "color": vf.LABEL_COLORS[name],
                         "shape": "cuboid_3d", "geometry_config": {}}
                        for n, name in enumerate(vf.CLASS_IDS)],
            "tags": [], "projectType": "point_clouds"}
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("meta.json", json.dumps(meta))
        bundle.writestr("key_id_map.json", json.dumps(key_ids))
        for frame, frame_key, objects, figures in import_frames:
            stem = frame["frame"] + ".pcd"
            ann = {"description": "auto-label draft; human review required", "key": frame_key,
                   "tags": [], "objects": objects, "figures": figures}
            bundle.writestr(f"ds0/ann/{stem}.json", json.dumps(ann))
            seq, index = vf.parse_frame_name(frame["frame"])
            lidar = data / f"sequence_{seq:02d}" / "lidar" / f"{seqs[seq][index]}.bin"
            bundle.writestr(f"ds0/pointcloud/{stem}", vf.bin_to_pcd(lidar))


if __name__ == "__main__":
    raise SystemExit(main())
