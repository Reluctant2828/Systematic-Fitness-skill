<h1 align="center">System Fitness Advisor.skill</h1>

<p align="center">
  <img src="./concept.png" alt="System Fitness Advisor Concept" width="900">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  <img src="https://img.shields.io/badge/Agent-Skill-purple.svg" alt="Agent Skill">
  <img src="https://img.shields.io/badge/Fitness-Knowledge_Base-green.svg" alt="Fitness Knowledge Base">
  <img src="https://img.shields.io/badge/Status-Maintained-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/Runtime-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Cursor%20%C2%B7%20OpenClaw%20%C2%B7%20Hermes-d946ef" alt="Runtime">
</p>

<p align="center">
  <strong>
    One skill for structured fitness planning, training analysis, and next-session decisions.<br>
    Your next coach does not have to be a human coach.
  </strong>
</p>

<p align="center">
  <sub>
    Built on the open <a href="https://agentskills.io/home">Agent Skills protocol</a>.
    Runs in Claude Code, Codex, Cursor, OpenClaw, Hermes Agent, CodeBuddy,
    Workbuddy, Gemini CLI, OpenCode, and 50+ compatible agent runtimes.
  </sub>
</p>

<p align="center">
  <strong>
    Most people do not fail because they are lazy.<br>
    They fail because they do not know what they should do next.<br>
    System Fitness Advisor.skill analyzes the user's goal, training age, equipment,
    schedule, history, and physical feedback to decide training structure, exercise
    selection, intensity, and progression, turning random workouts into systematic training.
  </strong>
</p>

<p align="center">
  <a href="#examples">Examples</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#what-problem-does-it-solve">Problems Solved</a> ·
  <a href="#algorithm-workflow">Algorithm</a>
</p>


## What Problem Does It Solve?

There are already plenty of fitness apps, workout trackers, and AI-generated training plans.

But the real problem for most trainees is not whether they have a plan.

It is this:

> I have been training for a while. What exactly should I change next time?

Many tools can record workouts. Many AI systems can generate templates. But they often fail on real training decisions:

- Historical training data is not saved, reused, or updated continuously, so every session feels like a first consultation.
- Barbells, dumbbells, machines, and shoulder isolation movements are forced into the same progression logic.
- When an exercise is missing from the library, the system either invents it or lets the plan break.
- Hypertrophy, fat loss, body recomposition, specialization, and powerlifting are treated as if they follow the same logic.
- Users upload training screenshots, but still do not know whether to increase weight, add reps, reduce load, or deload.

**System Fitness Advisor closes this gap:**

> From "what happened in training" to "what exactly should I do next time?"

---

## Examples

<strong>It does not just say "optimize your training." It tells you exactly what to do in the next session.</strong>

```text
User      > My bench press is currently 60 kg for 3 sets of 8 reps. What should I do next time?

fitness   > Barbell Bench Press: 60 kg x 3 sets x 9 reps

  Goal: first bring all 3 sets up to 9 reps. Do not rush the weight increase.

  If you complete 60 kg x 3x9 next time and RPE stays at or below 8.5:

  The following session should be 60 kg x 3x10.

  Once you can consistently complete 60 kg x 3x10:

  Increase to 65 kg, because barbell main lifts usually progress by +5 kg total load.
```

```text
User      > I completed 35 kg on the standing machine lateral raise. Can I go straight to 40 kg next time?

fitness   > I do not recommend jumping directly from 35 kg to 40 kg or higher.

  The standing machine lateral raise is a long-lever shoulder isolation movement.
  It should not progress like a bench press.

  For the next phase, keep 35 kg and make it more stable in the 12-15 rep range.
  Focus on controlled eccentrics, a brief pause at the top, or add a drop set.
```

Here is a fat-loss and recomposition example:

```text
User      > I have been dieting for two weeks, but my weight has not moved and my lifts are dropping.
            Should I keep eating less or add cardio?

fitness   > Do not immediately cut calories aggressively.

  You are seeing both weight stagnation and declining training performance,
  which is more likely a sign of elevated recovery stress.

  First confirm the trend using 7-day average body weight and waist measurement.

  If adherence is stable, prioritize a small increase in daily steps
  instead of cutting training volume further or adding a large amount of cardio.
```

---

## Installation

System Fitness Advisor is built on the open [Agent Skills](https://agentskills.io) protocol and can run in any skills-compatible AI agent runtime.

### Recommended: One-Line Installation

Open the agent runtime you use, such as Claude Code, Codex, Cursor, OpenClaw, Hermes, CodeBuddy, Gemini CLI, or OpenCode, and tell it:

```text
Install this skill for me: https://github.com/Reluctant2828/System-Fitness-Advisor-skill/tree/main/system-fitness-advisor
```

---

## Usage

After installation, tell your agent:

```text
/fitness
```

Then follow the prompts to enter your fitness information, such as height, weight, training experience, and training goal. For hypertrophy, you can also specify a preferred split, such as a 3-day, 4-day, or 5-day split. Then choose one or more data sources.

If you are not sure about any field, you can skip it. The system will start from a cold profile and refine itself over time.

### 1. Fitness Goal

Choose or describe your goal:

- Hypertrophy
- Fat loss and body recomposition
- Body-part specialization
- Powerlifting / strength improvement
- Not sure; let the system decide

### 2. Training Conditions

- How many days per week you can train
- How long each session can be
- Available gym equipment
- Whether you can only train at home
- Whether you already have a current training plan

### 3. Data Sources

You can provide one or more of the following:

- Direct text input
- Training screenshots
- CSV / spreadsheet files
- Fitness app exports
- Historical training logs
- Nutrition records
- Body metrics, such as body weight, waist measurement, progress photos, or body-fat estimates

If you do not have any historical data, you can skip this step.

### 4. Training Split

You can choose:

- 2-day split
- 3-day split / PPL
- 4-day split
- 5-day split
- Not sure; let the system recommend

If you do not understand training splits, System Fitness Advisor will automatically choose one based on your goal, weekly training frequency, recovery capacity, and training experience.

---

## Supported Data Sources

| Source | Supported | Notes |
|---|---:|---|
| Manual user input | Yes | Height, weight, goal, training experience, equipment conditions |
| Training logs | Yes | CSV/JSON are handled by the bundled importer; other readable exports can be analyzed manually by the runtime |
| Fitness app data | Yes | Xunji/训记 reads are read-only by default; write-back requires an explicit change summary and confirmation |
| Body assessment data | Yes | Body weight, measurements, body-fat estimates, strength performance |
| Nutrition records | Yes | Calories, protein, water intake, and eating habits |
| Sleep and recovery | Yes | Sleep duration, fatigue, soreness, and recovery feedback |
| Images / PDFs | Yes | Training sheets, body assessment reports, and screenshots |
| Pasted text | Yes | Current plans, logs, questions, or manual notes |

---

## Algorithm Logic

System Fitness Advisor does not simply generate a workout template.

Its core logic is:

> First understand who the user is, then identify the goal, read available data, and finally decide exactly what the user should do in the next session.

It starts from decision-making, not from templates.

### Decision Flow

System Fitness Advisor works in the following order:

```text
User input
  |
Identify user goal
  |
Detect available data sources
  |
Build user training profile
  |
Select training module
  |
Choose training split
  |
Match exercise library
  |
Apply real-world loading rules
  |
Generate next-session plan
  |
Continue adjusting based on future logs
```

---

## Built-In Algorithm Knowledge Base

System Fitness Advisor includes a fitness decision knowledge base that transforms user data into next-session training decisions.

### Included Modules

- **User profile knowledge base**  
  Stores height, weight, training age, goal, equipment, injury limitations, and other basic information.

- **Training log analysis**  
  Analyzes screenshots, CSV files, app exports, and text logs to decide whether the user should add load, add reps, reduce volume, or deload.

- **Body metrics analysis**  
  Analyzes body weight, waist measurement, progress photos, body-fat trends, and strength performance to assess fat loss, hypertrophy, or recovery status.

- **Nutrition log analysis**  
  Uses calories, protein, carbs, fat, and training performance to judge whether current nutrition supports the user's goal.

- **Hypertrophy knowledge base**  
  Supports 2-day, 3-day/PPL, 4-day, and 5-day splits, with decisions for volume, exercise selection, and progression.

- **Fat loss and recomposition knowledge base**  
  Evaluates calorie deficit, cardio, step count, training volume, and strength-retention strategy.

- **Body-part specialization knowledge base**  
  Supports specialization for chest, back, shoulders, arms, glutes, legs, calves, and other weak points.

- **Powerlifting knowledge base**  
  Supports squat, bench press, deadlift, e1RM, top singles, back-off sets, and periodized programming.

- **Exercise library**  
  Includes 147 exercises covering chest, back, shoulders, legs, arms, glutes, abs, and more.

- **Real-world loading rules**  
  Prevents unrealistic prescriptions, such as decimal machine loads, barbells below 20 kg, or blind weight jumps on shoulder isolation exercises.

### Core Goal

The purpose is not to generate a generic workout template.

The purpose is to answer:

> What should the user do next time, with which exercises, how much weight, how many sets, how many reps, and how should progression work?

---

## Algorithm Workflow

System Fitness Advisor follows a fixed training decision process:

1. **Read input**  
   Receive user profile, training logs, body metrics, nutrition records, screenshots, or other context.

2. **Identify goal**  
   Determine whether the current goal is hypertrophy, fat loss and recomposition, specialization, or powerlifting.

3. **Build profile**  
   Create a user profile based on training age, weekly frequency, available equipment, recovery status, and limitations.

4. **Select module**  
   Call the relevant knowledge base: hypertrophy, fat loss, specialization, or powerlifting.

5. **Choose split**  
   Select a 2-day, 3-day/PPL, 4-day, or 5-day split based on user conditions.  
   If the user is unsure, the system recommends one automatically.

6. **Match exercises**  
   Select exercises from the exercise library. If an exercise is missing, the system finds a same-slot substitute instead of pretending the missing exercise exists.

7. **Apply loading rules**  
   Check realistic constraints for barbells, dumbbells, machines, and isolation movements.

8. **Generate next session**  
   Output exercises, load, sets, reps, RPE/RIR, rest time, and progression rules.

9. **Continue updating**  
   Adjust the plan based on future training logs and user feedback.

Core logic:

> Analyze data first, identify the bottleneck, then prescribe the next concrete training step.

---

## Repository Structure

```text
system-fitness-advisor/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── data/
│   └── exercise-library.json
├── references/
│   ├── user-profile-intake.md
│   ├── user-data-management.md
│   ├── training-log-analysis.md
│   ├── body-metrics-analysis.md
│   ├── nutrition-log-analysis.md
│   ├── training-algorithm-library.md
│   ├── recommendation-decision-tree.md
│   ├── goal-hypertrophy.md
│   ├── goal-fat-loss-recomposition.md
│   ├── goal-specialization.md
│   ├── goal-powerlifting.md
│   ├── hypertrophy-splits.md
│   ├── ppl-practical.md
│   ├── split-two-division.md
│   ├── split-four-division.md
│   ├── split-five-division.md
│   ├── fat-loss-recomposition-advanced.md
│   ├── specialization-advanced.md
│   ├── powerlifting-advanced.md
│   └── exercise-library-schema.md
├── scripts/
│   ├── summarize_training_logs.py
│   └── manage_user_data.py
├── templates/
│   ├── user-intake.md
│   └── user-data/
│       ├── profile.json
│       ├── training-history.json
│       ├── body-metrics-history.json
│       └── nutrition-history.json
└── examples/
    ├── sample-training-log.csv
    ├── sample-nutrition-log.csv
    └── trigger-tests.md
```

---

## Notes

- This skill provides fitness planning and training recommendations. It is not a medical diagnosis tool.
- If you experience chest pain, dizziness, numbness, severe pain, or any other abnormal symptom, stop training and seek professional help.
- The `/fitness` command may conflict with other installed fitness skills. If necessary, keep only one fitness skill installed.
- Unknown fields can be skipped. The system will start from a cold profile and improve over time.
- If an exercise is not in the library, the system will not pretend it exists. It will mark it as an out-of-library exercise or suggest a same-slot substitute.
- Machine weights default to 5 kg increments and do not generate decimal machine loads.
- The minimum barbell load is the empty bar, 20 kg.
- Barbell main lifts default to +5 kg total-load progression.
- Dumbbell progression follows common dumbbell rack increments, usually +2.5 kg per hand.
- Shoulder isolation movements should not blindly jump in weight. Rep progression, control, density, or drop sets are preferred.
- Nutrition advice is only used to support training goals. It does not replace a registered dietitian, nutritionist, or physician.
- Historical user data should only be saved with user consent and should preferably be stored outside the skill folder.

---
