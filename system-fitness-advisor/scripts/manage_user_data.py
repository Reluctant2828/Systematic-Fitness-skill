#!/usr/bin/env python3
"""Manage portable user fitness data stores."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STORE_FILES = {
    "profile": ("profile.json", "profile"),
    "training": ("training-history.json", "training_logs"),
    "body": ("body-metrics-history.json", "body_metrics"),
    "nutrition": ("nutrition-history.json", "nutrition_logs"),
}

DEFAULT_STORES = {
    "profile": {
        "schema_version": "0.1",
        "profile": {
            "goal": "",
            "time_horizon": "",
            "age": None,
            "sex": "",
            "height_cm": None,
            "bodyweight_kg": None,
            "training_age": "",
            "weekly_training_days": None,
            "session_length_minutes": None,
            "equipment": [],
            "load_increments": {},
            "pain_constraints": [],
            "preferences": [],
            "must_keep_exercises": [],
            "disliked_exercises": [],
        },
        "current_program": {"split": "", "notes": ""},
        "updated_at": None,
        "notes": "",
    },
    "training": {"schema_version": "0.1", "training_logs": []},
    "body": {"schema_version": "0.1", "body_metrics": []},
    "nutrition": {"schema_version": "0.1", "nutrition_logs": []},
}

FIELD_ALIASES = {
    "date": ["date", "日期", "day", "created_at", "workout_date"],
    "session": ["session", "训练日", "课程", "workout", "workout_name", "split"],
    "status": ["status", "state", "状态", "完成状态", "done", "completed", "is_completed", "是否完成", "记录状态"],
    "exercise": ["exercise", "动作", "动作名称", "name", "exercise_name", "movement"],
    "sets": ["sets", "组", "组数", "set_count"],
    "reps": ["reps", "次数", "rep", "repetitions"],
    "load": ["load", "weight", "重量", "kg", "load_kg"],
    "rpe": ["rpe", "RPE", "强度"],
    "rir": ["rir", "RIR", "余力"],
    "body_part": ["body_part", "部位", "肌群", "target", "muscle"],
    "bodyweight": ["bodyweight", "bodyweight_kg", "体重", "weight", "体重kg"],
    "waist": ["waist", "waist_cm", "腰围", "腰围cm"],
    "steps": ["steps", "步数"],
    "cardio_minutes": ["cardio_minutes", "cardio", "有氧", "有氧分钟"],
    "sleep_hours": ["sleep_hours", "sleep", "睡眠", "睡眠小时"],
    "meal": ["meal", "餐次", "meal_name"],
    "food": ["food", "食物", "food_name", "name"],
    "quantity": ["quantity", "份量", "amount", "serving"],
    "calories": ["calories", "kcal", "热量", "卡路里"],
    "protein_g": ["protein_g", "protein", "蛋白质", "蛋白"],
    "carbs_g": ["carbs_g", "carbs", "碳水", "碳水化合物"],
    "fat_g": ["fat_g", "fat", "脂肪"],
    "fiber_g": ["fiber_g", "fiber", "膳食纤维", "纤维"],
    "hunger": ["hunger", "饥饿感"],
    "adherence": ["adherence", "执行度", "达成度"],
    "notes": ["notes", "备注", "comment", "comments"],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm_key(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def first_value(row: dict[str, Any], canonical: str) -> Any:
    normalized = {norm_key(str(key)): value for key, value in row.items()}
    for alias in FIELD_ALIASES[canonical]:
        key = norm_key(alias)
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    return None


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    return float(match.group(0)) if match else None


def parse_date(value: Any) -> str:
    if value in (None, ""):
        return ""
    text = str(value).strip()
    text = re.sub(r"[年月]", "-", text).replace("日", "")
    text = text.replace(".", "-").replace("/", "-")
    text = text.split("T")[0].strip()
    for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d-%Y"]:
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text).date().isoformat()
    except ValueError:
        return text


def normalize_status(value: Any) -> tuple[str, bool]:
    """Keep planned/skipped rows distinct from completed training evidence."""
    if value in (None, ""):
        return "completed", True
    if isinstance(value, bool):
        return ("completed" if value else "planned"), False
    text = norm_key(str(value))
    if text in {"completed", "complete", "done", "finished", "已完成", "完成", "已做", "true", "yes", "1", "是"}:
        return "completed", False
    if text in {"planned", "plan", "scheduled", "计划", "已计划", "待完成", "未完成", "false", "no", "0", "否"}:
        return "planned", False
    if text in {"skipped", "skip", "missed", "cancelled", "canceled", "跳过", "未训练", "缺席", "取消"}:
        return "skipped", False
    return "unknown", False


def flatten_json(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        rows: list[dict[str, Any]] = []
        for item in data:
            rows.extend(flatten_json(item))
        return rows
    if not isinstance(data, dict):
        return []
    for key in ["training_logs", "nutrition_logs", "body_metrics", "logs", "records", "rows"]:
        if isinstance(data.get(key), list):
            return flatten_json(data[key])
    return [data]


def read_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".json":
        return flatten_json(json.loads(path.read_text(encoding="utf-8-sig")))
    raise ValueError(f"Unsupported input format: {suffix}. Use CSV or JSON.")


def store_path(store_dir: Path, kind: str) -> Path:
    return store_dir / STORE_FILES[kind][0]


def load_store(store_dir: Path, kind: str) -> dict[str, Any]:
    path = store_path(store_dir, kind)
    if not path.exists():
        return json.loads(json.dumps(DEFAULT_STORES[kind]))
    return json.loads(path.read_text(encoding="utf-8"))


def save_store(store_dir: Path, kind: str, data: dict[str, Any], backup: bool = False) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    path = store_path(store_dir, kind)
    if backup and path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(path, path.with_name(f"{path.name}.bak-{stamp}"))
    payload = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=store_dir, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temp_name = handle.name
            handle.write(payload)
            handle.flush()
        Path(temp_name).replace(path)
    finally:
        if temp_name:
            temp_path = Path(temp_name)
            if temp_path.exists():
                temp_path.unlink()


def stable_id(record_type: str, record: dict[str, Any]) -> str:
    payload = {key: value for key, value in record.items() if key not in ("_entry_id", "imported_at")}
    encoded = json.dumps({"type": record_type, "record": payload}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(encoded.encode("utf-8")).hexdigest()[:16]


def clean_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if value not in (None, "")}


def canonical_training(row: dict[str, Any], source: str) -> dict[str, Any]:
    status, status_inferred = normalize_status(first_value(row, "status"))
    return clean_record(
        {
            "date": parse_date(first_value(row, "date")),
            "session": first_value(row, "session"),
            "exercise": first_value(row, "exercise"),
            "status": status,
            "status_inferred": status_inferred,
            "sets": first_value(row, "sets"),
            "reps": first_value(row, "reps"),
            "load": parse_float(first_value(row, "load")),
            "rpe": parse_float(first_value(row, "rpe")),
            "rir": parse_float(first_value(row, "rir")),
            "body_part": first_value(row, "body_part"),
            "notes": first_value(row, "notes"),
            "source_file": source,
            "raw": row,
        }
    )


def canonical_body(row: dict[str, Any], source: str) -> dict[str, Any]:
    return clean_record(
        {
            "date": parse_date(first_value(row, "date")),
            "bodyweight_kg": parse_float(first_value(row, "bodyweight")),
            "waist_cm": parse_float(first_value(row, "waist")),
            "steps": parse_float(first_value(row, "steps")),
            "cardio_minutes": parse_float(first_value(row, "cardio_minutes")),
            "sleep_hours": parse_float(first_value(row, "sleep_hours")),
            "notes": first_value(row, "notes"),
            "source_file": source,
            "raw": row,
        }
    )


def canonical_nutrition(row: dict[str, Any], source: str) -> dict[str, Any]:
    return clean_record(
        {
            "date": parse_date(first_value(row, "date")),
            "meal": first_value(row, "meal"),
            "food": first_value(row, "food"),
            "quantity": first_value(row, "quantity"),
            "calories": parse_float(first_value(row, "calories")),
            "protein_g": parse_float(first_value(row, "protein_g")),
            "carbs_g": parse_float(first_value(row, "carbs_g")),
            "fat_g": parse_float(first_value(row, "fat_g")),
            "fiber_g": parse_float(first_value(row, "fiber_g")),
            "hunger": first_value(row, "hunger"),
            "adherence": first_value(row, "adherence"),
            "notes": first_value(row, "notes"),
            "source_file": source,
            "raw": row,
        }
    )


def append_records(store_dir: Path, kind: str, records: list[dict[str, Any]], backup: bool = False) -> tuple[int, int]:
    data = load_store(store_dir, kind)
    list_key = STORE_FILES[kind][1]
    existing = data.setdefault(list_key, [])
    existing_ids = {item.get("_entry_id") for item in existing if isinstance(item, dict)}
    imported_at = now_iso()
    added = 0
    skipped = 0
    for record in records:
        if not record:
            continue
        record["_entry_id"] = stable_id(kind, record)
        record["imported_at"] = imported_at
        if record["_entry_id"] in existing_ids:
            skipped += 1
            continue
        existing.append(record)
        existing_ids.add(record["_entry_id"])
        added += 1
    data["updated_at"] = imported_at
    save_store(store_dir, kind, data, backup=backup)
    return added, skipped


def import_rows(store_dir: Path, kind: str, input_path: Path, backup: bool = False) -> tuple[int, int]:
    rows = read_rows(input_path)
    source = input_path.name
    if kind == "training":
        records = [canonical_training(row, source) for row in rows]
    elif kind == "body":
        records = [canonical_body(row, source) for row in rows]
    elif kind == "nutrition":
        records = [canonical_nutrition(row, source) for row in rows]
    else:
        raise ValueError(f"Unsupported import type: {kind}")
    return append_records(store_dir, kind, records, backup=backup)


def date_range(records: list[dict[str, Any]]) -> str:
    dates = sorted(record.get("date") for record in records if record.get("date"))
    if not dates:
        return "unknown"
    return f"{dates[0]} to {dates[-1]}"


def avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 1) if values else None


def render_summary(store_dir: Path) -> str:
    training = load_store(store_dir, "training").get("training_logs", [])
    body = load_store(store_dir, "body").get("body_metrics", [])
    nutrition = load_store(store_dir, "nutrition").get("nutrition_logs", [])

    nutrition_by_date: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in nutrition:
        date = row.get("date") or "unknown"
        for field in ["calories", "protein_g", "carbs_g", "fat_g", "fiber_g"]:
            value = row.get(field)
            if isinstance(value, (int, float)):
                nutrition_by_date[date][field] += float(value)

    daily_calories = [totals["calories"] for totals in nutrition_by_date.values() if totals.get("calories")]
    daily_protein = [totals["protein_g"] for totals in nutrition_by_date.values() if totals.get("protein_g")]
    bodyweights = [row["bodyweight_kg"] for row in body if isinstance(row.get("bodyweight_kg"), (int, float))]
    waist_values = [row["waist_cm"] for row in body if isinstance(row.get("waist_cm"), (int, float))]
    state_counts = {state: 0 for state in ["completed", "planned", "skipped", "unknown"]}
    for row in training:
        state = row.get("status") or "completed"
        state_counts[state if state in state_counts else "unknown"] += 1

    lines = ["# User Data Summary", ""]
    lines.append(f"- Store: {store_dir}")
    lines.append(f"- Training records: {len(training)} ({date_range(training)})")
    lines.append(
        f"- Training states: completed={state_counts['completed']}, planned={state_counts['planned']}, skipped={state_counts['skipped']}, unknown={state_counts['unknown']}"
    )
    lines.append(f"- Body metric records: {len(body)} ({date_range(body)})")
    lines.append(f"- Nutrition records: {len(nutrition)} ({date_range(nutrition)})")
    lines.append(f"- Avg daily calories: {avg(daily_calories) if daily_calories else 'unknown'}")
    lines.append(f"- Avg daily protein: {avg(daily_protein) if daily_protein else 'unknown'} g")
    lines.append(f"- Avg bodyweight: {avg(bodyweights) if bodyweights else 'unknown'} kg")
    lines.append(f"- Avg waist: {avg(waist_values) if waist_values else 'unknown'} cm")
    lines.append("")
    lines.append("## Next analysis")
    lines.append("- Use `summarize_training_logs.py training-history.json` for detailed training trend analysis.")
    lines.append("- Use `nutrition-log-analysis.md` with this summary for diet decisions tied to training goals.")
    return "\n".join(lines)


def init_store(store_dir: Path) -> None:
    store_dir.mkdir(parents=True, exist_ok=True)
    for kind in STORE_FILES:
        path = store_path(store_dir, kind)
        if not path.exists():
            save_store(store_dir, kind, DEFAULT_STORES[kind])


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage portable user fitness data stores.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create an empty user data store.")
    init_parser.add_argument("store_dir", type=Path)

    for command, kind, help_text in [
        ("import-training", "training", "Import workout logs into training-history.json."),
        ("import-body", "body", "Import body metrics into body-metrics-history.json."),
        ("import-nutrition", "nutrition", "Import nutrition logs into nutrition-history.json."),
    ]:
        subparser = subparsers.add_parser(command, help=help_text)
        subparser.add_argument("store_dir", type=Path)
        subparser.add_argument("input", type=Path)
        subparser.add_argument("--backup", action="store_true", help="Back up the target JSON before importing.")
        subparser.set_defaults(kind=kind)

    summary_parser = subparsers.add_parser("summary", help="Print a user data store summary.")
    summary_parser.add_argument("store_dir", type=Path)

    args = parser.parse_args()

    if args.command == "init":
        init_store(args.store_dir)
        print(f"Initialized user data store: {args.store_dir}")
        return 0

    if args.command in {"import-training", "import-body", "import-nutrition"}:
        init_store(args.store_dir)
        added, skipped = import_rows(args.store_dir, args.kind, args.input, backup=args.backup)
        backup_note = "; backup created" if args.backup else ""
        print(f"Imported {added} records into {STORE_FILES[args.kind][0]}; skipped {skipped} duplicates{backup_note}.")
        return 0

    if args.command == "summary":
        print(render_summary(args.store_dir))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
