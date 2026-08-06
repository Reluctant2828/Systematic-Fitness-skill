#!/usr/bin/env python3
"""Summarize workout logs for the System Fitness Advisor skill."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


FIELD_ALIASES = {
    "date": ["date", "日期", "训练日期", "day", "workout_date", "created_at"],
    "session": ["session", "训练日", "课程", "workout", "workout_name", "split"],
    "status": ["status", "state", "状态", "完成状态", "done", "completed", "is_completed", "是否完成", "记录状态"],
    "exercise": ["exercise", "动作", "动作名称", "name", "exercise_name", "movement"],
    "sets": ["sets", "组", "组数", "set_count"],
    "reps": ["reps", "次数", "rep", "重复", "repetitions"],
    "load": ["load", "weight", "重量", "kg", "重量kg", "load_kg"],
    "rpe": ["rpe", "RPE", "强度"],
    "rir": ["rir", "RIR", "余力"],
    "body_part": ["body_part", "部位", "肌群", "target", "muscle"],
    "notes": ["notes", "备注", "comment", "comments"],
}


@dataclass
class SetRecord:
    date: datetime | None
    week: str
    session: str
    exercise: str
    library_exercise: str
    match_type: str
    match_candidates: tuple[str, ...]
    body_part: str
    movement_pattern: str
    equipment: str
    reps: float | None
    load: float | None
    rpe: float | None
    rir: float | None
    hard_set: bool
    assumed_hard: bool
    matched: bool
    status: str
    status_inferred: bool
    row_key: str
    invalid_fields: tuple[str, ...] = ()
    uncertain_fields: tuple[str, ...] = ()


@dataclass
class ExerciseMatch:
    meta: dict[str, Any]
    matched: bool
    library_exercise: str
    match_type: str
    candidates: tuple[str, ...] = ()


def norm_key(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


EXERCISE_ALIASES = {
    norm_key("卧推"): ["杠铃卧推"],
    norm_key("平板卧推"): ["杠铃卧推"],
    norm_key("杠铃平板卧推"): ["杠铃卧推"],
    norm_key("上斜卧推"): ["上斜杠铃卧推", "上斜哑铃卧推", "上斜史密斯卧推"],
    norm_key("上斜哑铃推"): ["上斜哑铃卧推"],
    norm_key("哑铃上斜卧推"): ["上斜哑铃卧推"],
    norm_key("哑铃侧平举"): ["哑铃飞鸟"],
    norm_key("器械侧平举"): ["站姿器械侧平举"],
    norm_key("站姿侧平举"): ["站姿器械侧平举", "哑铃飞鸟", "绳索侧平举"],
    norm_key("侧平举"): ["哑铃飞鸟", "绳索侧平举", "站姿器械侧平举"],
    norm_key("反向飞鸟"): ["蝴蝶机反向飞鸟"],
    norm_key("后束飞鸟"): ["蝴蝶机反向飞鸟"],
    norm_key("坐姿划船机"): ["坐姿划船"],
    norm_key("绳索划船"): ["坐姿划船"],
    norm_key("坐姿绳索划船"): ["坐姿划船"],
    norm_key("划船"): ["杠铃划船", "坐姿划船", "悍马机划船"],
    norm_key("高位下拉"): ["宽距高位下拉"],
    norm_key("下拉"): ["宽距高位下拉", "窄距下拉", "对握高位下拉"],
    norm_key("RDL"): ["挂片式罗马尼亚硬拉", "史密斯罗马尼亚硬拉"],
    norm_key("罗马尼亚硬拉"): ["挂片式罗马尼亚硬拉", "史密斯罗马尼亚硬拉"],
    norm_key("传统硬拉"): ["硬拉"],
    norm_key("直腿硬拉"): ["史密斯机直腿硬拉", "绳索直腿硬拉"],
    norm_key("保加利亚蹲"): ["哑铃保加利亚蹲"],
    norm_key("哈克蹲"): ["哈克深蹲"],
    norm_key("腿举"): ["器械倒蹬"],
    norm_key("倒蹬"): ["器械倒蹬"],
    norm_key("腿屈伸"): ["坐姿腿屈伸"],
    norm_key("腿伸展"): ["坐姿腿屈伸"],
    norm_key("绳索下压"): ["直杆绳索下压"],
    norm_key("三头下压"): ["直杆绳索下压"],
    norm_key("臂屈伸"): ["器械臂屈伸", "绳索臂屈伸", "仰卧杠铃臂屈伸"],
    norm_key("绳索弯举"): ["直杆绳索弯举"],
    norm_key("二头弯举"): ["杠铃弯举", "哑铃弯举", "直杆绳索弯举"],
    norm_key("臀推"): ["史密斯臀冲"],
    norm_key("臀桥"): ["史密斯臀冲"],
    norm_key("卷腹"): ["绳索跪姿卷腹", "站姿绳索卷腹", "悍马机卷腹", "坐姿器械卷腹", "触膝卷腹"],
}


def first_value(row: dict[str, Any], canonical: str) -> Any:
    normalized = {norm_key(str(key)): value for key, value in row.items()}
    for alias in FIELD_ALIASES[canonical]:
        key = norm_key(alias)
        if key in normalized and normalized[key] not in (None, ""):
            return normalized[key]
    return None


def parse_date(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    text = re.sub(r"[年月]", "-", text).replace("日", "")
    text = text.replace(".", "-").replace("/", "-")
    text = text.split("T")[0].strip()
    formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def parse_numbers(value: Any) -> list[float]:
    if value in (None, ""):
        return []
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return []
        return [float(value)]
    text = str(value).replace("\u2013", "-").replace("\u2014", "-")
    single_range = re.fullmatch(r"\s*[-+]?\d+(?:\.\d+)?\s*-\s*[-+]?\d+(?:\.\d+)?\s*", text)
    if single_range:
        match = re.search(r"[-+]?\d+(?:\.\d+)?", text)
        return [float(match.group(0))] if match else []
    text = re.sub(r"(?<=\d)\s*-\s*(?=\d)", ",", text)
    return [float(match) for match in re.findall(r"-?\d+(?:\.\d+)?", text)]


def is_single_range(value: Any) -> bool:
    if value in (None, ""):
        return False
    text = str(value).replace("\u2013", "-").replace("\u2014", "-")
    return bool(re.fullmatch(r"\s*[-+]?\d+(?:\.\d+)?\s*-\s*[-+]?\d+(?:\.\d+)?\s*", text))


def normalize_for_key(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_for_key(child) for key, child in value.items() if key is not None}
    if isinstance(value, list):
        return [normalize_for_key(child) for child in value]
    if isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r"[-+]?\d+(?:\.\d+)?", text):
            try:
                number = float(text)
                return int(number) if number.is_integer() else number
            except ValueError:
                pass
        return text
    return value


def row_fingerprint(row: dict[str, Any]) -> str:
    payload = {
        norm_key(str(key)): normalize_for_key(value)
        for key, value in row.items()
        if key is not None and norm_key(str(key)) not in {"source_file", "imported_at", "_entry_id", "__row_key"}
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(encoded.encode("utf-8")).hexdigest()[:16]


def deduplicate_rows(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    unique: list[dict[str, Any]] = []
    seen: set[str] = set()
    duplicates = 0
    for row in rows:
        key = row_fingerprint(row)
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        unique.append({**row, "__row_key": key})
    return unique, duplicates


def parse_int(value: Any, default: int = 1) -> int:
    nums = parse_numbers(value)
    if not nums:
        return default
    return max(0, int(round(nums[0])))


def parse_float(value: Any) -> float | None:
    nums = parse_numbers(value)
    return nums[0] if nums else None


def classify_status(value: Any, default_status: str = "unknown") -> tuple[str, bool]:
    """Normalize common app/export status values without treating plans as completed."""
    if value in (None, ""):
        return default_status, True
    if isinstance(value, bool):
        return ("completed" if value else "planned"), False
    text = norm_key(str(value))
    if text in {"completed", "complete", "done", "finished", "已完成", "完成", "已做", "true", "yes", "1", "是"}:
        return "completed", False
    if text in {"planned", "plan", "scheduled", "计划", "已计划", "待完成", "false", "no", "0", "否"}:
        return "planned", False
    if text in {"skipped", "skip", "missed", "cancelled", "canceled", "跳过", "未训练", "缺席", "取消"}:
        return "skipped", False
    return "unknown", False


def iso_week(date_value: datetime | None) -> str:
    if not date_value:
        return "unknown-week"
    year, week, _ = date_value.isocalendar()
    return f"{year}-W{week:02d}"


def load_library(path: Path) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    exercises = data.get("exercises", []) if isinstance(data, dict) else []
    library: dict[str, list[dict[str, Any]]] = {}
    for exercise in exercises:
        name = str(exercise.get("name_zh", "")).strip()
        if name:
            library.setdefault(norm_key(name), []).append(exercise)
    return library


def exercise_name(exercise: dict[str, Any]) -> str:
    return str(exercise.get("name_zh", "")).strip()


def unique_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = str(candidate.get("id") or exercise_name(candidate))
        if candidate_id in seen:
            continue
        seen.add(candidate_id)
        unique.append(candidate)
    return unique


def infer_body_part_from_name(name: str) -> str:
    text = norm_key(name)
    if any(token in text for token in ["侧平举", "推肩", "推举", "后束", "反向飞鸟", "面拉"]):
        return "肩"
    if any(token in text for token in ["卧推", "夹胸", "推胸"]):
        return "胸"
    if "飞鸟" in text and not any(token in text for token in ["后束", "反向", "侧平举"]):
        return "胸"
    if any(token in text for token in ["下拉", "划船", "引体", "直臂下压"]):
        return "背"
    if any(token in text for token in ["深蹲", "腿举", "倒蹬", "腿屈伸", "腿弯举", "腿伸展"]):
        return "腿"
    if any(token in text for token in ["臀", "髋", "罗马尼亚", "硬拉", "早安", "驴踢", "后踢"]):
        return "臀部"
    if any(token in text for token in ["弯举", "二头"]):
        return "二头"
    if any(token in text for token in ["三头", "下压", "臂屈伸"]):
        return "三头"
    if any(token in text for token in ["卷腹", "抬腿", "转体", "触膝"]):
        return "腹部"
    return ""


def context_matches(exercise: dict[str, Any], body_part_input: str) -> bool:
    if not body_part_input:
        return False
    needle = norm_key(body_part_input)
    values = [
        str(exercise.get("body_part", "")),
        str(exercise.get("body_part_id", "")),
        str(exercise.get("equipment", "")),
        str(exercise.get("equipment_id", "")),
        *[str(value) for value in exercise.get("primary_muscles", [])],
    ]
    return any(needle and (needle in norm_key(value) or norm_key(value) in needle) for value in values if value)


def pick_candidate(candidates: list[dict[str, Any]], body_part_input: str) -> dict[str, Any] | None:
    if len(candidates) == 1:
        return candidates[0]
    contextual = [candidate for candidate in candidates if context_matches(candidate, body_part_input)]
    if len(contextual) == 1:
        return contextual[0]
    return None


def common_meta(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    inferred: dict[str, Any] = {}
    for field in ["body_part", "movement_pattern", "equipment"]:
        values = {str(candidate.get(field, "")).strip() for candidate in candidates if candidate.get(field)}
        if len(values) == 1:
            inferred[field] = values.pop()
    return inferred


def resolve_exercise(
    exercise_name_input: str,
    library: dict[str, list[dict[str, Any]]],
    body_part_input: str = "",
) -> ExerciseMatch:
    key = norm_key(exercise_name_input)
    context = body_part_input or infer_body_part_from_name(exercise_name_input)
    exact_candidates = unique_candidates(library.get(key, []))
    picked_exact = pick_candidate(exact_candidates, context)
    if picked_exact:
        return ExerciseMatch(picked_exact, True, exercise_name(picked_exact), "exact")
    if exact_candidates:
        names = tuple(sorted({exercise_name(candidate) for candidate in exact_candidates}))
        return ExerciseMatch(common_meta(exact_candidates), False, "", "ambiguous_exact", names)

    alias_candidates = unique_candidates(
        [
            candidate
            for name in EXERCISE_ALIASES.get(key, [])
            for candidate in library.get(norm_key(name), [])
        ]
    )
    picked_alias = pick_candidate(alias_candidates, context)
    if picked_alias:
        return ExerciseMatch(picked_alias, True, exercise_name(picked_alias), "alias")
    if alias_candidates:
        names = tuple(sorted({exercise_name(candidate) for candidate in alias_candidates}))
        return ExerciseMatch(common_meta(alias_candidates), False, "", "ambiguous_alias", names)

    near_candidates = unique_candidates(
        [
            exercise
            for library_key, exercises in library.items()
            if key and (key in library_key or library_key in key)
            for exercise in exercises
        ]
    )
    picked_near = pick_candidate(near_candidates, context)
    if picked_near:
        return ExerciseMatch(picked_near, True, exercise_name(picked_near), "unique_near_name")
    if near_candidates:
        names = tuple(sorted({exercise_name(candidate) for candidate in near_candidates}))
        return ExerciseMatch(common_meta(near_candidates), False, "", "ambiguous_near_name", names)

    return ExerciseMatch({}, False, "", "unmatched")


def flatten_json(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, list):
        rows: list[dict[str, Any]] = []
        for item in data:
            rows.extend(flatten_json(item))
        return rows
    if not isinstance(data, dict):
        return []

    for key in ["logs", "training_logs", "records", "rows"]:
        if isinstance(data.get(key), list):
            return flatten_json(data[key])

    workouts = data.get("workouts") or data.get("sessions")
    if isinstance(workouts, list):
        rows = []
        for workout in workouts:
            if not isinstance(workout, dict):
                continue
            base = {k: v for k, v in workout.items() if k not in ("exercises", "sets")}
            exercises = workout.get("exercises", [])
            if isinstance(exercises, list):
                for exercise in exercises:
                    if not isinstance(exercise, dict):
                        continue
                    exercise_base = {**base, **{k: v for k, v in exercise.items() if k != "sets"}}
                    sets = exercise.get("sets")
                    if isinstance(sets, list):
                        for set_row in sets:
                            if isinstance(set_row, dict):
                                rows.append({**exercise_base, **set_row})
                    else:
                        rows.append(exercise_base)
        return rows

    return [data]


def read_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, restkey="__extra_columns__")
            rows = list(reader)
            if reader.fieldnames and any(not str(name).strip() for name in reader.fieldnames):
                raise ValueError("CSV contains an empty header name; fix the export before analysis.")
            if any("__extra_columns__" in row for row in rows):
                raise ValueError("CSV contains more values than headers; fix the export before analysis.")
            return rows
    if suffix == ".json":
        return flatten_json(json.loads(path.read_text(encoding="utf-8-sig")))
    raise ValueError(f"Unsupported input format: {suffix}. Use CSV or JSON.")


def expand_sets(rows: list[dict[str, Any]], library: dict[str, list[dict[str, Any]]], default_status: str = "unknown") -> list[SetRecord]:
    records: list[SetRecord] = []
    for row in rows:
        exercise_name = str(first_value(row, "exercise") or "").strip()
        if not exercise_name:
            continue

        date_value = parse_date(first_value(row, "date"))
        session = str(first_value(row, "session") or "").strip()
        body_part_input = str(first_value(row, "body_part") or "").strip()
        status, status_inferred = classify_status(first_value(row, "status"), default_status)
        exercise_match = resolve_exercise(exercise_name, library, body_part_input)
        exercise_meta = exercise_match.meta

        body_part = body_part_input or str(exercise_meta.get("body_part", "unknown"))
        movement_pattern = str(exercise_meta.get("movement_pattern", "unknown"))
        equipment = str(exercise_meta.get("equipment", "unknown"))

        sets_count = parse_int(first_value(row, "sets"), default=0)
        reps_values = parse_numbers(first_value(row, "reps"))
        load_value = parse_float(first_value(row, "load"))
        rpe_values = parse_numbers(first_value(row, "rpe"))
        rir_values = parse_numbers(first_value(row, "rir"))

        invalid_fields: list[str] = []
        uncertain_fields: list[str] = []
        for field in ("reps", "load", "rpe", "rir"):
            if is_single_range(first_value(row, field)):
                uncertain_fields.append(field)
        if load_value is not None and load_value < 0:
            invalid_fields.append("load")
            load_value = None
        if any(value <= 0 for value in reps_values):
            invalid_fields.append("reps")
            reps_values = []
        if any(value < 0 or value > 10 for value in rpe_values):
            invalid_fields.append("rpe")
            rpe_values = []
        if any(value < 0 or value > 10 for value in rir_values):
            invalid_fields.append("rir")
            rir_values = []
        raw_sets = first_value(row, "sets")
        if raw_sets not in (None, "") and (not parse_numbers(raw_sets) or any(value <= 0 for value in parse_numbers(raw_sets))):
            invalid_fields.append("sets")

        if sets_count <= 0:
            sets_count = len(reps_values) if reps_values else 1
        if not reps_values:
            reps_values = [None] * sets_count  # type: ignore[list-item]
        elif len(reps_values) == 1 and sets_count > 1:
            reps_values = reps_values * sets_count
        else:
            sets_count = max(sets_count, len(reps_values))
            reps_values = reps_values + [reps_values[-1]] * (sets_count - len(reps_values))

        for index in range(sets_count):
            reps = reps_values[index]
            rpe = rpe_values[index] if index < len(rpe_values) else (rpe_values[0] if rpe_values else None)
            rir = rir_values[index] if index < len(rir_values) else (rir_values[0] if rir_values else None)
            assumed_hard = rpe is None and rir is None
            hard_set = assumed_hard or (rpe is not None and rpe >= 6) or (rir is not None and rir <= 4)
            records.append(
                SetRecord(
                    date=date_value,
                    week=iso_week(date_value),
                    session=session,
                    exercise=exercise_name,
                    library_exercise=exercise_match.library_exercise,
                    match_type=exercise_match.match_type,
                    match_candidates=exercise_match.candidates,
                    body_part=body_part or "unknown",
                    movement_pattern=movement_pattern,
                    equipment=equipment,
                    reps=reps,
                    load=load_value,
                    rpe=rpe,
                    rir=rir,
                    hard_set=hard_set,
                    assumed_hard=assumed_hard,
                    matched=exercise_match.matched,
                    status=status,
                    status_inferred=status_inferred,
                    row_key=str(row.get("__row_key") or row_fingerprint(row)),
                    invalid_fields=tuple(sorted(set(invalid_fields))),
                    uncertain_fields=tuple(sorted(set(uncertain_fields))),
                )
            )
    return records


def epley_1rm(load: float | None, reps: float | None) -> float | None:
    if load is None or reps is None or load <= 0 or reps <= 0 or reps > 12:
        return None
    return load * (1 + reps / 30)


def summarize(
    records: list[SetRecord],
    duplicate_row_count: int = 0,
    input_row_count: int | None = None,
    dropped_row_count: int = 0,
) -> dict[str, Any]:
    status_counts = {status: sum(1 for record in records if record.status == status) for status in ["completed", "planned", "skipped", "unknown"]}
    status_record_counts = {
        status: len({record.row_key for record in records if record.status == status})
        for status in status_counts
    }
    analysis_records = [record for record in records if record.status == "completed"]
    trend_records = [record for record in analysis_records if record.date]
    dated = [record.date for record in analysis_records if record.date]
    summary: dict[str, Any] = {
        "input_row_count": input_row_count if input_row_count is not None else len({record.row_key for record in records}),
        "duplicate_row_count": duplicate_row_count,
        "dropped_row_count": dropped_row_count,
        "record_count": len({record.row_key for record in records}),
        "completed_record_count": status_record_counts["completed"],
        "set_count": len(records),
        "completed_set_count": len(analysis_records),
        "excluded_set_count": len(records) - len(analysis_records),
        "status_counts": status_counts,
        "status_record_counts": status_record_counts,
        "status_inferred_set_count": sum(1 for record in records if record.status_inferred),
        "status_inferred_record_count": len({record.row_key for record in records if record.status_inferred}),
        "invalid_field_count": sum(1 for record in records if record.invalid_fields),
        "uncertain_value_count": sum(1 for record in records if record.uncertain_fields),
        "undated_completed_set_count": len(analysis_records) - len(trend_records),
        "date_start": min(dated).date().isoformat() if dated else None,
        "date_end": max(dated).date().isoformat() if dated else None,
        "weeks": sorted({record.week for record in trend_records}),
        "unresolved_exercises": sorted({record.exercise for record in records if record.match_type.startswith("ambiguous_")}),
        "unmatched_exercises": sorted({record.exercise for record in records if record.match_type == "unmatched"}),
    }
    match_rows = {}
    for record in records:
        match_rows.setdefault(
            record.exercise,
            {
                "exercise": record.exercise,
                "matched_library": record.matched,
                "match_type": record.match_type,
                "library_exercise": record.library_exercise,
                "candidates": list(record.match_candidates),
            },
        )
    summary["exercise_matches"] = sorted(match_rows.values(), key=lambda row: row["exercise"])

    weekly: dict[tuple[str, str], dict[str, Any]] = {}
    for record in trend_records:
        key = (record.week, record.body_part)
        bucket = weekly.setdefault(
            key,
            {
                "week": record.week,
                "body_part": record.body_part,
                "completed_sets": 0,
                "hard_sets": 0,
                "assumed_hard_sets": 0,
                "volume_load": 0.0,
                "session_dates": set(),
                "exercises": set(),
            },
        )
        bucket["completed_sets"] += 1
        bucket["hard_sets"] += 1 if record.hard_set else 0
        bucket["assumed_hard_sets"] += 1 if record.assumed_hard else 0
        if record.load is not None and record.reps is not None:
            bucket["volume_load"] += record.load * record.reps
        if record.date:
            bucket["session_dates"].add(record.date.date().isoformat())
        bucket["exercises"].add(record.exercise)

    weekly_rows = []
    for bucket in weekly.values():
        weekly_rows.append(
            {
                "week": bucket["week"],
                "body_part": bucket["body_part"],
                "completed_sets": bucket["completed_sets"],
                "hard_sets": bucket["hard_sets"],
                "assumed_hard_sets": bucket["assumed_hard_sets"],
                "frequency": len(bucket["session_dates"]),
                "volume_load": round(bucket["volume_load"], 1),
                "exercises": sorted(bucket["exercises"]),
            }
        )
    summary["weekly_body_part_summary"] = sorted(weekly_rows, key=lambda row: (row["week"], row["body_part"]))

    exercise_buckets: dict[str, list[SetRecord]] = defaultdict(list)
    for record in trend_records:
        exercise_buckets[record.exercise].append(record)

    exercise_rows = []
    for exercise, exercise_records in exercise_buckets.items():
        exercise_records = sorted(exercise_records, key=lambda item: item.date or datetime.min)
        dated_sessions = sorted({record.date.date().isoformat() for record in exercise_records if record.date})
        one_rms = [epley_1rm(record.load, record.reps) for record in exercise_records]
        one_rms = [value for value in one_rms if value is not None]
        rpes = [record.rpe for record in exercise_records if record.rpe is not None]
        session_e1rms: dict[str, list[float]] = defaultdict(list)
        for record in exercise_records:
            e1rm = epley_1rm(record.load, record.reps)
            if e1rm is not None:
                session_key = record.date.date().isoformat() if record.date else (record.session or record.row_key)
                session_e1rms[session_key].append(e1rm)
        session_peaks = [max(values) for _, values in sorted(session_e1rms.items())]
        first = session_peaks[0] if session_peaks else None
        last = session_peaks[-1] if session_peaks else None
        exercise_rows.append(
            {
                "exercise": exercise,
                "body_part": exercise_records[0].body_part,
                "movement_pattern": exercise_records[0].movement_pattern,
                "matched_library": exercise_records[0].matched,
                "match_type": exercise_records[0].match_type,
                "library_exercise": exercise_records[0].library_exercise,
                "match_candidates": list(exercise_records[0].match_candidates),
                "sessions": len(dated_sessions) if dated_sessions else len({record.session for record in exercise_records}),
                "hard_sets": sum(1 for record in exercise_records if record.hard_set),
                "best_load": max((record.load or 0 for record in exercise_records), default=0),
                "best_e1rm": round(max(one_rms), 1) if one_rms else None,
                "first_recent_e1rm": round(first, 1) if first else None,
                "last_recent_e1rm": round(last, 1) if last else None,
                "avg_rpe": round(sum(rpes) / len(rpes), 1) if rpes else None,
            }
        )
    summary["exercise_summary"] = sorted(exercise_rows, key=lambda row: (row["body_part"], row["exercise"]))

    flags = []
    if status_counts["planned"]:
        flags.append({"type": "planned_records_excluded", "message": "Planned records were excluded from completed-work trend calculations."})
    if status_counts["planned"] or status_counts["skipped"] or status_counts["unknown"]:
        flags.append(
            {
                "type": "record_states_present",
                "completed": status_counts["completed"],
                "planned": status_counts["planned"],
                "skipped": status_counts["skipped"],
                "unknown": status_counts["unknown"],
            }
        )
    if records and not analysis_records:
        flags.append({"type": "no_completed_records", "message": "No completed records were available for progression analysis."})
    if summary["unresolved_exercises"]:
        flags.append({"type": "unresolved_exercises", "message": "Some exercises need confirmation before treating them as library matches."})
    if summary["unmatched_exercises"]:
        flags.append({"type": "unmatched_exercises", "message": "Some exercises have no library candidate."})
    if summary["invalid_field_count"]:
        invalid_fields = sorted({field for record in records for field in record.invalid_fields})
        flags.append({"type": "invalid_input_values", "fields": invalid_fields, "records": summary["invalid_field_count"]})
    if summary["uncertain_value_count"]:
        uncertain_fields = sorted({field for record in records for field in record.uncertain_fields})
        flags.append({"type": "range_values_lower_bound", "fields": uncertain_fields, "records": summary["uncertain_value_count"]})
    if summary["undated_completed_set_count"]:
        flags.append({"type": "undated_completed_records", "sets": summary["undated_completed_set_count"], "message": "Completed records without dates were excluded from dated trend calculations."})
    if summary["dropped_row_count"]:
        flags.append({"type": "dropped_input_rows", "rows": summary["dropped_row_count"], "message": "Input rows without a usable exercise were excluded."})
    for row in summary["exercise_matches"]:
        if row["match_type"].startswith("ambiguous_"):
            flags.append(
                {
                    "type": row["match_type"],
                    "exercise": row["exercise"],
                    "candidates": row["candidates"],
                }
            )
    for row in summary["weekly_body_part_summary"]:
        if row["hard_sets"] >= 20:
            flags.append({"type": "high_weekly_volume", "body_part": row["body_part"], "week": row["week"], "hard_sets": row["hard_sets"]})
        if row["hard_sets"] > 0 and row["frequency"] <= 1 and row["hard_sets"] >= 12:
            flags.append({"type": "single_day_volume_cluster", "body_part": row["body_part"], "week": row["week"], "hard_sets": row["hard_sets"]})
    for row in summary["exercise_summary"]:
        if row["avg_rpe"] is not None and row["avg_rpe"] >= 9:
            flags.append({"type": "high_average_rpe", "exercise": row["exercise"], "avg_rpe": row["avg_rpe"]})
        if row["first_recent_e1rm"] and row["last_recent_e1rm"] and row["sessions"] >= 3:
            if row["last_recent_e1rm"] < row["first_recent_e1rm"] * 0.97:
                flags.append({"type": "possible_performance_drop", "exercise": row["exercise"]})
    summary["flags"] = flags
    return summary


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown(summary: dict[str, Any]) -> str:
    lines = ["# Training Log Summary", ""]
    lines.append(f"- Source rows: {summary['input_row_count']} (unique analyzed rows: {summary['record_count']}; exact duplicates removed: {summary['duplicate_row_count']}; dropped: {summary['dropped_row_count']})")
    lines.append(f"- Sets parsed: {summary['set_count']}")
    lines.append(f"- Completed sets used for trends: {summary['completed_set_count']}")
    counts = summary["status_counts"]
    lines.append(
        f"- Set states: completed={counts['completed']}, planned={counts['planned']}, skipped={counts['skipped']}, unknown={counts['unknown']}"
    )
    record_counts = summary["status_record_counts"]
    lines.append(
        f"- Source-row states: completed={record_counts['completed']}, planned={record_counts['planned']}, skipped={record_counts['skipped']}, unknown={record_counts['unknown']}"
    )
    if summary["status_inferred_set_count"]:
        lines.append(f"- Missing status inferred: {summary['status_inferred_set_count']} sets across {summary['status_inferred_record_count']} source rows")
    lines.append(f"- Date range: {summary.get('date_start') or 'unknown'} to {summary.get('date_end') or 'unknown'}")
    lines.append(f"- Weeks: {', '.join(summary['weeks']) if summary['weeks'] else 'unknown'}")
    if summary["unresolved_exercises"]:
        lines.append(f"- Unresolved exercises: {', '.join(summary['unresolved_exercises'])}")
    if summary["unmatched_exercises"]:
        lines.append(f"- Unmatched exercises: {', '.join(summary['unmatched_exercises'])}")
    lines.append("")

    lines.append("## Exercise Library Matches")
    match_rows = [
        [
            row["exercise"],
            row["match_type"],
            row["library_exercise"],
            ", ".join(row["candidates"]),
        ]
        for row in summary["exercise_matches"]
    ]
    lines.append(markdown_table(["Exercise", "Match type", "Library exercise", "Candidates"], match_rows))
    lines.append("")

    lines.append("## Weekly Body-Part Summary")
    weekly_rows = [
        [
            row["week"],
            row["body_part"],
            row["completed_sets"],
            row["hard_sets"],
            row["assumed_hard_sets"],
            row["frequency"],
            row["volume_load"],
            ", ".join(row["exercises"]),
        ]
        for row in summary["weekly_body_part_summary"]
    ]
    lines.append(markdown_table(["Week", "Body part", "Sets", "Hard sets", "Assumed hard", "Frequency", "Volume load", "Exercises"], weekly_rows))
    lines.append("")

    lines.append("## Exercise Summary")
    exercise_rows = [
        [
            row["exercise"],
            row["body_part"],
            row["movement_pattern"],
            row["sessions"],
            row["hard_sets"],
            row["best_load"],
            row["best_e1rm"],
            row["avg_rpe"],
            "yes" if row["matched_library"] else "no",
            row["match_type"],
            row["library_exercise"],
        ]
        for row in summary["exercise_summary"]
    ]
    lines.append(markdown_table(["Exercise", "Body part", "Pattern", "Sessions", "Hard sets", "Best load", "Best e1RM", "Avg RPE", "Library", "Match type", "Library exercise"], exercise_rows))
    lines.append("")

    lines.append("## Flags")
    if summary["flags"]:
        for flag in summary["flags"]:
            details = ", ".join(f"{key}={value}" for key, value in flag.items() if key != "message")
            if flag.get("message"):
                lines.append(f"- {flag['message']} ({details})")
            else:
                lines.append(f"- {details}")
    else:
        lines.append("- No automatic flags.")
    lines.append("")
    lines.append("## Notes")
    lines.append("- Only completed records drive weekly volume, frequency, progression, and e1RM trends; planned/skipped/unknown records remain excluded.")
    lines.append("- Hard sets are assumed when RPE/RIR is missing.")
    lines.append("- Exercise matching uses exact names, curated aliases, and unique near-name matches; ambiguous candidates stay flagged for review.")
    lines.append("- Volume load is load x reps and is context only; do not treat it as better than technique, RPE/RIR, or target tension.")
    lines.append("- A single range such as 8-10 is reported using its lower bound and flagged as uncertain; it is not evidence of two completed sets.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize workout logs for System Fitness Advisor.")
    parser.add_argument("input", type=Path, help="CSV or JSON workout log file.")
    parser.add_argument("--library", type=Path, default=Path(__file__).resolve().parents[1] / "data" / "exercise-library.json")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument(
        "--default-status",
        choices=["unknown", "completed", "planned", "skipped"],
        default="unknown",
        help="Status for rows without a status field. Use completed only after verifying the source is a completed-log export.",
    )
    parser.add_argument("--output", type=Path, help="Optional output path.")
    args = parser.parse_args()

    raw_rows = read_rows(args.input)
    rows, duplicate_row_count = deduplicate_rows(raw_rows)
    library = load_library(args.library)
    records = expand_sets(rows, library, default_status=args.default_status)
    represented_row_keys = {record.row_key for record in records}
    dropped_row_count = sum(1 for row in rows if str(row.get("__row_key") or row_fingerprint(row)) not in represented_row_keys)
    summary = summarize(
        records,
        duplicate_row_count=duplicate_row_count,
        input_row_count=len(raw_rows),
        dropped_row_count=dropped_row_count,
    )
    output = json.dumps(summary, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(summary)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = output.encode("utf-8")
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile("wb", dir=args.output.parent, prefix=f".{args.output.name}.", suffix=".tmp", delete=False) as handle:
                temp_name = handle.name
                handle.write(payload)
                handle.flush()
            Path(temp_name).replace(args.output)
        finally:
            if temp_name and Path(temp_name).exists():
                Path(temp_name).unlink()
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
