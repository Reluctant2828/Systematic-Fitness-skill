# Recommendation Decision Tree

Use this reference after profile, training-log, body-metric, and goal-module analysis to choose the smallest useful recommendation: keep, progress, add volume, reduce fatigue, change exercise, change split, run specialization, deload, or ask for missing data.

## Primary rule

Make the smallest change that solves the bottleneck. Do not rewrite the entire plan when a progression rule, volume adjustment, exercise order change, or deload is enough.

## Decision order

1. Safety: pain, red flags, medical symptoms.
2. Goal: hypertrophy, fat loss, specialization, powerlifting, mixed.
3. Data confidence: logs/body metrics exact, partial, or sparse.
4. Bottleneck: use one canonical enum: `under_stimulus`, `over_fatigue`, `technique_mismatch`, `recovery`, `adherence`, `equipment_mismatch`, `goal_mismatch`, `missing_data`, `plateau`, `progression_gap`, `split_mismatch`, `exercise_redundancy`, `weak_point`, or `safety_flag`.
5. Action: choose one primary change and one optional secondary change.
6. Tracking: define 2-6 week evidence needed to reassess.

## Safety gate

| Signal | Action |
|---|---|
| Chest pain, fainting, severe dizziness, severe neurological symptoms, or another emergency warning sign | Stop normal programming immediately and advise local emergency services or urgent evaluation. |
| Sharp/radiating pain, numbness, or persistent unusual pain | Stop the provoking movement and seek qualified clinical evaluation. |
| Joint discomfort only on one movement | Modify load/range, swap close variation, reduce provocative volume. |
| General soreness/fatigue | Adjust volume, RPE, rest, or deload based on performance trend. |

## Data confidence

| Data state | Recommendation style |
|---|---|
| Rich logs + metrics | Narrow diagnosis and specific changes. |
| Logs but no RPE/recovery | Diagnose volume/frequency/progression; ask for RPE and fatigue next. |
| Metrics but no logs | Discuss body trend; ask for training data before changing program deeply. |
| Goal only | Give conservative starter plan and request minimum fields. |
| Unclear screenshots | State uncertainty and avoid exact claims. |

## Bottleneck to action

| Bottleneck | Signs | Primary action |
|---|---|---|
| `under_stimulus` | Recovery good, target not progressing, low volume/frequency | Add 1-2 sets/week or one exposure. |
| `over_fatigue` | Multiple lifts down, soreness/sleep/joints poor | Reduce volume 20-40% or deload. |
| `technique_mismatch` | Target not felt, compensation rises | Change cues, load, exercise stability, or order. |
| `recovery` | Sleep, stress, soreness, or readiness is limiting work | Reduce stress and protect key movements. |
| `adherence` | Planned frequency or nutrition is not repeatable | Simplify the plan and solve the limiting habit. |
| `equipment_mismatch` | Planned loads impossible, machine jumps invalid | Adjust increments or choose same-slot available movement. |
| `goal_mismatch` | The current plan serves a different primary goal | Re-rank the goal before changing exercises. |
| `missing_data` | No reliable completion, trend, or constraint evidence | Ask the minimum high-impact question or start conservatively. |
| `plateau` | 2-3 weeks without body or performance change after adherence check | Follow the appropriate small adjustment order. |
| `progression_gap` | The same work repeats without a clear rep/load/RIR rule | Add a measurable progression rule before changing the movement. |
| `split_mismatch` | Schedule is inconsistent or body parts are repeatedly missed | Choose the simplest split that fits actual availability. |
| `exercise_redundancy` | Several movements fill the same slot without adding signal | Consolidate and keep the most trackable pain-free option. |
| `weak_point` | One body part lags despite adequate general training | Run a bounded priority block and reduce non-target fatigue. |
| `safety_flag` | Red-flag symptom or pain boundary | Stop normal programming and route to safety-only output. |

## Action menu

### Keep plan

Use when progress is occurring and fatigue is acceptable.

Output: continue, define next progression threshold, track same metrics.

### Add reps or load

Use when all sets hit the top of the rep range at target RPE/RIR.

Rules:

- Barbell main lifts: default +5 kg total.
- Dumbbells: default +2.5 kg per hand if rack unknown.
- Machines: default +5 kg, no decimals or unsupported 2.5 kg jumps.
- Shoulder isolations: reps/control/density before load.

### Add volume or frequency

Use when recovery is good and target stimulus is low.

Rules:

- Add 1-2 hard sets/week to target muscle.
- Add exposure before cramming all volume into one session.
- Reduce non-target volume if adding target volume creates recovery conflict.

### Reduce fatigue

Use when performance or recovery is worsening.

Options:

- Reduce sets 20-40% for 1 week.
- Keep movement but raise RIR by 1-2.
- Remove advanced techniques first.
- Reduce accessory work before key lifts unless key lifts cause pain.
- Deload if multiple fatigue signals exist.

### Change exercise

Use when:

- Target muscle is not loaded despite cue changes.
- Equipment is unavailable.
- Pain/joint irritation appears.
- Progression has stalled because the movement no longer fits the user.

Do not use when:

- The only reason is that progression is hard to calculate.
- The movement is effective and simply needs better progression.

### Change split

Use when:

- User cannot adhere to current weekly schedule.
- Frequency is too low for the goal.
- Session length is too long and quality drops.
- Recovery cannot handle the split.

Do not change split just because another split sounds more advanced.

### Run specialization

Use when one or two target muscles are clear weak points and recovery can be reallocated.

Rules:

- Target muscle 12-24 hard sets/week depending on level and recovery.
- Non-target muscles 4-8 sets/week maintenance.
- Block length 4-8 weeks.
- Exit if target improves, recovery fails, pain rises, or progress stalls.

### Deload

Use when two or more are present:

- Key lifts down repeatedly.
- Soreness or joint irritation persists.
- Sleep/recovery stress high.
- 4-8 hard weeks completed.
- Technique worsens under normal loads.

Default: cut sets 30-50%, reduce load 5-15%, keep movement patterns, stay farther from failure.

## Mixed-goal handling

| Mixed goal | Primary logic | Secondary logic |
|---|---|---|
| Hypertrophy + fat loss | Fat-loss module if deficit/scale is central | Maintain hypertrophy stimulus and strength. |
| Hypertrophy + weak point | Hypertrophy split plus specialization insertion | Reduce non-target volume. |
| Powerlifting + hypertrophy | Powerlifting main lifts first | Accessories use hypertrophy/specialization rules. |
| Fat loss + powerlifting | Strength preservation and fatigue control | Avoid aggressive deficits near tests. |
| Body shaping + local weak point | Fat-loss/body-metric trend plus target muscle block | Do not promise local fat loss. |

## Output decision format

When using this reference, inherit the selected output profile from `SKILL.md`. At minimum, output `结论` and `数据状态`, include the canonical bottleneck id plus its Chinese explanation, and include `下一次训练` only when the user asked for planning or log review. Include the canonical exercise-match fields when an exercise is discussed.

When using this reference, output:

```text
结论:
主要瓶颈:
证据:
本次只改:
不改什么:
接下来 2-6 周观察:
需要补充:
```

Use "不改什么" to prevent unnecessary program rewrites when the current plan mostly works.
