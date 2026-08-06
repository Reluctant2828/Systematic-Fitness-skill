# Training Log Analysis

Use this reference when the user provides workout logs, screenshots, app exports, API data, or text records and asks what is wrong, whether the plan is working, how to modify the plan, or why progress has stalled.

## Purpose

Turn training records into program decisions. Prefer actual completed work over intended plans.

## Script support

For CSV or JSON logs, run `scripts/summarize_training_logs.py` before making the coaching judgment when the file is available locally.

Example:

```bash
python scripts/summarize_training_logs.py examples/sample-training-log.csv
python scripts/summarize_training_logs.py user-log.json --format json
```

Accepted CSV/JSON field aliases include:

- Date: `date`, `日期`, `训练日期`, `day`, `workout_date`.
- Exercise: `exercise`, `动作`, `动作名称`, `name`, `exercise_name`.
- Sets/reps/load: `sets`, `组数`, `reps`, `次数`, `load`, `weight`, `重量`.
- Intensity: `rpe`, `RPE`, `rir`, `RIR`.
- Record state: `status`, `state`, `状态`, `done`, `completed`, `is_completed`. Normalize to `completed`, `planned`, `skipped`, or `unknown`.
- Optional: `session`, `训练日`, `body_part`, `部位`, `notes`.

Use the script output as a structured summary, not as the final answer. The coaching conclusion still comes from this reference plus the goal module and `recommendation-decision-tree.md`.

Only completed records should drive volume, frequency, progression, and e1RM trends. The script reports `status_counts` and excludes planned, skipped, and unknown sets from those calculations. If a source omits status, the script marks the completed status as inferred; confirm that the export represents completed work before making a progression decision.

Exercise names are matched in this order:

1. Exact `data/exercise-library.json` name.
2. Exact duplicate resolution by user-provided body part or inferred body part from the exercise name.
3. Curated aliases such as `哑铃侧平举 -> 哑铃飞鸟`, `高位下拉 -> 宽距高位下拉`, `腿举 -> 器械倒蹬`, `臀推 -> 史密斯臀冲`, and `RDL -> 罗马尼亚硬拉` candidates.
4. Unique near-name match when only one library exercise clearly contains the requested name.
5. Ambiguous candidate list when several library exercises could fit.
6. Unmatched when no reasonable library candidate exists.

Treat `exact`, `ambiguous_exact`, `alias`, `unique_near_name`, `ambiguous_alias`, `ambiguous_near_name`, and `unmatched` differently in the final coaching answer. `unresolved_exercises` means the exact library exercise still needs confirmation; `unmatched_exercises` means no library candidate exists. Do not present ambiguous or unmatched exercises as confirmed library entries; either ask the user to confirm the exact variation or use the outside-library fallback.

## Data extraction

Extract each workout into:

```text
date:
session_name:
exercise:
body_part:
movement_pattern:
equipment:
sets:
reps:
load:
volume_load:
RPE/RIR:
rest:
notes:
pain/fatigue:
status: completed | planned | skipped | unknown
```

If screenshots are uncertain, mark uncertain values instead of treating them as exact.

## Evidence hierarchy

| Evidence | Reliability |
|---|---|
| 4-8 weeks of dated logs with sets/reps/load/RPE | Highest |
| 2-3 weeks of dated logs | Useful trend |
| One week of logs | Snapshot only |
| Plan without completion records | Intent, not proof |
| User memory without details | Use cautiously |
| App screenshots with cropped/unclear values | Extract but mark uncertainty |

## Core calculations

| Metric | How to use |
|---|---|
| Weekly hard sets per muscle | Main volume signal. Count sets that are close enough to failure and technically valid. |
| Frequency per muscle | Number of weekly exposures; not just number of exercises. |
| Rep-range distribution | Shows whether work matches strength, hypertrophy, isolation, or pump goals. |
| Load trend | Detects progression, regression, or stalled load. |
| Rep trend at same load | Often more useful than load alone. |
| RPE/RIR trend | Shows whether progression is real or just more effort. |
| Session order | Detects weak-point neglect or fatigue interference. |
| Exercise redundancy | Detects too many same-pattern movements. |
| Recovery signal | Performance drops, soreness, joint feedback, sleep, motivation. |

Volume-load is useful for context but should not override quality, RPE/RIR, range of motion, or target-muscle tension.

## Weekly set targets by goal

Use goal references for final ranges. As a diagnostic starting point:

| Goal | Diagnostic set range |
|---|---|
| General hypertrophy | Major muscles often 8-16 hard sets/week; trained users may need 10-20. |
| Fat loss/recomposition | Often 8-14 hard sets/week when recovery is limited. |
| Specialization | Target muscle often 12-24 hard sets/week; non-targets 4-8. |
| Powerlifting | Count SBD competition and close-variation volume separately from bodybuilding accessories. |

## Progress classification

| Pattern | Diagnosis | Likely action |
|---|---|---|
| Same load, more reps, same/lower RPE | Good progress | Keep plan; small progression. |
| Higher load, same reps, same RPE | Good progress | Keep plan; monitor recovery. |
| Same performance but lower bodyweight in cut | Good fat-loss preservation | Keep key lifts, manage fatigue. |
| Load/reps flat for 2-4 weeks, recovery good | Under-stimulus or stale progression | Add reps/sets/frequency or change progression rule. |
| Load/reps down for 2+ sessions with high fatigue | Overreaching/recovery issue | Reduce volume 20-40% or deload. |
| Target muscle not improving but synergists sore | Execution mismatch | Change exercise/cues before adding volume. |
| Joint pain rises before muscle fatigue | Safety/equipment mismatch | Substitute or reduce provocative pattern. |
| Every set near failure and performance drops | Failure overuse | Raise RIR and reduce accessory volume. |
| Many exercises, few trackable sets | Low signal plan | Consolidate to stable movements. |

## Plateau diagnosis

Do not call a plateau from one bad session.

Hypertrophy plateau likely when:

- 3-6 weeks without rep/load improvement on key target movements.
- Target weekly volume/frequency are appropriate.
- Recovery and adherence are acceptable.
- Technique and range are stable.

Fatigue plateau likely when:

- Multiple lifts regress together.
- Warm-ups feel heavy.
- Soreness, sleep, motivation, or joint stress worsens.
- Volume or failure frequency recently increased.

Skill/technique plateau likely when:

- Load increases only with shorter range, more swing, or target-muscle loss.
- User reports "没有感觉" in the target muscle.
- Video/screenshot notes suggest compensation.

## Movement balance checks

| Area | Red flag |
|---|---|
| Upper body | Push volume far exceeds pull volume for long periods. |
| Back | Only rows or only pulldowns; no distinction between lat width and mid-back. |
| Shoulders | Pressing only, little side/rear delt work. |
| Legs | Squat/leg press only; missing hinge, leg curl, calves, unilateral stability. |
| Arms | Only indirect work despite explicit arm goal. |
| Core | Only crunches when bracing/anti-rotation is needed for lifting goals. |

## Load progression checks

Apply equipment rules from `training-algorithm-library.md` after diagnosis:

- Fixed machines default to 5 kg jumps.
- Barbell main lifts default to +5 kg total jumps.
- Dumbbells usually +2.5 kg per hand when rack increments are unknown.
- Long-lever shoulder isolations progress reps/control/density before load.
- Do not replace an exercise only because progression math is inconvenient.

## Output requirements

When using this reference, include:

- Data range and confidence: exact, partial, screenshot-uncertain, or sparse.
- Key findings: volume, frequency, intensity, progression, fatigue, exercise selection.
- The primary bottleneck: under-stimulus, over-fatigue, technique mismatch, adherence, or goal mismatch.
- The smallest useful change for the next 2-6 weeks.
- What to track next: target lifts, reps, RPE, body metrics, soreness, sleep, pain, adherence.
