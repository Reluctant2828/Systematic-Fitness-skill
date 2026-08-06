#!/usr/bin/env python3
"""Validate a portable System Fitness Advisor user-data store without changing it."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


STORE_FILES = {
    "profile": ("profile.json", "profile"),
    "training": ("training-history.json", "training_logs"),
    "body": ("body-metrics-history.json", "body_metrics"),
    "nutrition": ("nutrition-history.json", "nutrition_logs"),
}
ALLOWED_STATUS = {"completed", "planned", "skipped", "unknown"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|token|authorization|bearer|password|passwd|cookie|secret|credential|private[_-]?key)",
    re.I,
)


def load_json(path: Path, issues: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(f"{path.name}: invalid JSON ({exc})")
        return None


def inspect_secret_keys(value: Any, location: str, issues: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text):
                issues.append(f"{location}.{key_text}: secret-like key must not be stored in the user-data package")
            inspect_secret_keys(child, f"{location}.{key_text}", issues)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            inspect_secret_keys(child, f"{location}[{index}]", issues)


def numeric_values(value: Any) -> list[float] | None:
    if value in (None, ""):
        return []
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return [float(value)]
    if isinstance(value, str):
        text = re.sub(r"(?<=\d)\s*[-\u2013\u2014]\s*(?=\d)", ",", value.strip())
        matches = re.findall(r"[-+]?\d+(?:\.\d+)?", text)
        return [float(item) for item in matches] if matches else None
    return None


def validate_records(records: Any, list_key: str, filename: str, issues: list[str], warnings: list[str]) -> int:
    if not isinstance(records, list):
        issues.append(f"{filename}.{list_key}: expected a list")
        return 0

    entry_ids: set[str] = set()
    for index, record in enumerate(records):
        location = f"{filename}.{list_key}[{index}]"
        if not isinstance(record, dict):
            issues.append(f"{location}: expected an object")
            continue
        entry_id = record.get("_entry_id")
        if entry_id:
            entry_id_text = str(entry_id)
            if entry_id_text in entry_ids:
                issues.append(f"{location}._entry_id: duplicate entry ID")
            entry_ids.add(entry_id_text)
        else:
            warnings.append(f"{location}: missing _entry_id; imported records may not deduplicate safely")

        if list_key == "training_logs":
            if not str(record.get("exercise", "")).strip():
                issues.append(f"{location}.exercise: required for training records")
            status = record.get("status")
            if status not in ALLOWED_STATUS:
                issues.append(f"{location}.status: expected one of {sorted(ALLOWED_STATUS)}")
            if "status_inferred" in record and not isinstance(record["status_inferred"], bool):
                issues.append(f"{location}.status_inferred: expected boolean")

            for field in ("sets", "reps", "load", "rpe", "rir"):
                values = numeric_values(record.get(field))
                if values is None:
                    issues.append(f"{location}.{field}: expected numeric value")
                elif field in {"sets", "reps"} and any(value <= 0 for value in values):
                    issues.append(f"{location}.{field}: expected positive value")
                elif field in {"load"} and any(value < 0 for value in values):
                    issues.append(f"{location}.{field}: cannot be negative")

        date_value = record.get("date")
        if date_value:
            if not DATE_RE.match(str(date_value)):
                issues.append(f"{location}.date: expected YYYY-MM-DD")
            else:
                try:
                    date.fromisoformat(str(date_value))
                except ValueError:
                    issues.append(f"{location}.date: invalid calendar date")

        numeric_fields = {
            "training_logs": ("load", "rpe", "rir"),
            "body_metrics": ("bodyweight_kg", "waist_cm", "steps", "cardio_minutes", "sleep_hours"),
            "nutrition_logs": ("calories", "protein_g", "carbs_g", "fat_g", "fiber_g"),
        }.get(list_key, ())
        if list_key == "body_metrics" and not any(record.get(field) is not None for field in numeric_fields):
            issues.append(f"{location}: at least one body metric is required")
        if list_key == "nutrition_logs" and not any(record.get(field) is not None for field in numeric_fields) and not any(record.get(field) for field in ("meal", "food", "quantity")):
            issues.append(f"{location}: at least one nutrition value or meal/food field is required")
        for field in numeric_fields:
            value = record.get(field)
            if value is None:
                continue
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                issues.append(f"{location}.{field}: expected a number")
                continue
            if value < 0:
                issues.append(f"{location}.{field}: cannot be negative")
        if list_key == "training_logs":
            for field in ("rpe", "rir"):
                value = record.get(field)
                if isinstance(value, (int, float)) and not isinstance(value, bool) and not 0 <= value <= 10:
                    issues.append(f"{location}.{field}: expected 0-10")

    return len(records)


def validate_store(store_dir: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}

    if not store_dir.exists() or not store_dir.is_dir():
        issues.append(f"store directory does not exist: {store_dir}")
        return {"valid": False, "issues": issues, "warnings": warnings, "counts": counts}

    for kind, (filename, list_key) in STORE_FILES.items():
        path = store_dir / filename
        if not path.exists():
            issues.append(f"missing required file: {filename}")
            continue
        data = load_json(path, issues)
        if not isinstance(data, dict):
            continue
        if not data.get("schema_version"):
            warnings.append(f"{filename}: schema_version is missing")
        if kind == "profile":
            if not isinstance(data.get("profile"), dict):
                issues.append(f"{filename}.profile: expected an object")
            counts[kind] = 1
        else:
            counts[kind] = validate_records(data.get(list_key), list_key, filename, issues, warnings)
        inspect_secret_keys(data, filename, issues)

    return {"valid": not issues, "issues": issues, "warnings": warnings, "counts": counts}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a portable user fitness data store without changing it.")
    parser.add_argument("store_dir", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = validate_store(args.store_dir)
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        state = "valid" if result["valid"] else "invalid"
        print(f"Store is {state}: {args.store_dir}")
        print(f"Counts: {result['counts']}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
        for issue in result["issues"]:
            print(f"ERROR: {issue}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
