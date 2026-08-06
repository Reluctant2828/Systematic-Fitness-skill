# Training Algorithm Library

Use this reference when turning user fitness data into a program decision. Treat all values as coaching ranges, not medical prescriptions.

## Data hierarchy

Prefer evidence in this order:

1. User's latest actual training logs, symptoms, constraints, and corrections.
2. Recent trend over 2-6 weeks.
3. Stated goal, schedule, equipment, and preferences.
4. General programming ranges below.

## Safety gate

Stop normal programming and give a safety-first answer when the user reports sharp pain, numbness, radiating pain, dizziness, fainting, chest pain, or severe unusual symptoms. For chest pain, fainting, severe dizziness, or severe neurological symptoms, advise local emergency services or urgent evaluation. For other sharp/radiating/persistent pain, stop the provoking movement and recommend qualified clinical evaluation. Do not diagnose.

## Goal modules

Use the dedicated goal modules for detailed programming:

- `goal-hypertrophy.md`: hypertrophy, muscle size, and recoverable effective volume.
- `goal-fat-loss-recomposition.md`: fat loss, body shaping, recomposition, and muscle retention.
- `goal-specialization.md`: focused blocks for one or two body parts or weak points.
- `goal-powerlifting.md`: SBD, max strength, peaking, and meet-style training.

This file only holds shared rules that apply across all goals.

## Load and equipment constraints

These are hard constraints. Apply them after choosing exercises and before outputting any planned load or progression.

- Fixed machines default to 5 kg increments. Do not output 2.5 kg jumps or decimal machine weights unless the user explicitly says that machine supports them.
- Barbell work starts no lower than the empty bar: 20 kg total.
- Main barbell lifts such as bench press progress by total +5 kg by default.
- Dumbbells follow the user's actual rack increments; assume each hand +2.5 kg when unknown.
- Long-lever shoulder isolations, especially standing machine lateral raise, must not jump linearly from 35 kg directly to 40 kg or above. Progress reps, drop sets, tempo/control, pause quality, or rest-density before load.
- Do not replace an exercise only because the algorithm has difficulty calculating its progression. Same-slot substitutions are allowed only when the user chooses them, the equipment is unavailable, or a safety/pain constraint requires it; state the reason.

## Adjustment rules

### Add stimulus when recovery is good

If performance is stable or rising, soreness is manageable, and the target muscle is not progressing, choose one:

- Add 1-2 hard sets per week to the target muscle.
- Add one target exposure if frequency is low.
- Add reps within the current range.
- Add load only after reps and technique meet the rule.

### Reduce fatigue when recovery is poor

If performance drops for 2+ sessions, motivation is low, soreness lingers, sleep is poor, or joints feel irritated, choose one:

- Reduce volume by 20-40% for 1 week.
- Keep load but reduce sets or RPE.
- Swap the painful or stale exercise for a close variation.
- Add a deload before starting a new block.

### Deload triggers

Use a deload when two or more are present:

- Repeated performance decline across key lifts.
- Persistent soreness or joint irritation.
- Sleep/recovery stress is high.
- The user has pushed hard for 4-8 weeks.
- Technique quality is worsening under normal loads.

Deload options: cut sets by 30-50%, reduce load by 5-15%, keep movement patterns, and stop sets farther from failure.

## Plan construction

1. Set weekly training days and session length first.
2. Assign split by goal and availability: full body for 2-3 days, upper/lower for 4 days, PPL or specialization split for 5-6 days.
3. Put high-skill or high-load compounds early.
4. Balance movement patterns: squat/lunge, hinge, horizontal push/pull, vertical push/pull, isolation, trunk.
5. Match exercise choices to equipment and pain-free execution.
6. Define progression and deload rules before listing optional accessories.

## Output calibration

When data is sparse, give a conservative starting plan and ask for logs after 2-4 weeks. When data is rich, explain the specific trend and make narrower changes.
