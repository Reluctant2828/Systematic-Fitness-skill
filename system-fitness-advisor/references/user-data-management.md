# User Data Management

Use this reference when the user asks to save, import, update, persist, review, or reuse long-term fitness data such as profile, training history, body metrics, or nutrition logs.

## Purpose

Maintain a portable user data store that works across Agent Skills-compatible runtimes without requiring a database.

## Data store layout

Use a folder outside the skill package for real user data, for example `user-data/` in the current project or another user-approved location.

```text
user-data/
  profile.json
  training-history.json
  body-metrics-history.json
  nutrition-history.json
```

Do not store private user data inside the reusable skill folder unless the user explicitly asks for a local demo fixture.

## Script support

Use `scripts/manage_user_data.py` when the runtime can execute Python:

```bash
python scripts/manage_user_data.py init user-data
python scripts/manage_user_data.py import-training user-data workout-log.csv
python scripts/manage_user_data.py import-body user-data body-metrics.csv
python scripts/manage_user_data.py import-nutrition user-data nutrition-log.csv
# Add --backup to any import when the target JSON already contains user data.
python scripts/manage_user_data.py import-training user-data workout-log.csv --backup
python scripts/manage_user_data.py summary user-data
```

The script uses only the Python standard library, writes through a temporary file, and deduplicates repeated imports with stable entry IDs. `--backup` copies the target JSON to a timestamped `.bak-*` file before an import.

If Python execution is unavailable, create or update the JSON files manually using the templates in `templates/user-data/`.

## Data types

| File | Purpose | Main consumers |
|---|---|---|
| `profile.json` | Goal, schedule, training age, equipment, constraints, preferences | `user-profile-intake.md`, all goal modules |
| `training-history.json` | Completed workouts and imported logs | `training-log-analysis.md`, `summarize_training_logs.py` |
| `body-metrics-history.json` | Weight, waist, measurements, photos, steps, sleep, cardio | `body-metrics-analysis.md` |
| `nutrition-history.json` | Meals, calories, macros, hunger, adherence notes | `nutrition-log-analysis.md`, fat-loss module |

## Update rules

- Ask before creating or modifying a long-term user data folder.
- Preserve raw imported fields under `raw` when possible.
- Keep imported records append-only unless the user asks to correct or delete an entry.
- Preserve training `status` as `completed`, `planned`, `skipped`, or `unknown`; only completed records count as progression evidence.
- If the source has no status field, store `status_inferred: true` and treat the completion state as lower-confidence until confirmed.
- Mark uncertain screenshot extraction with `confidence: "screenshot_uncertain"`.
- Never expose API keys or private secrets in saved JSON.
- When data conflicts, keep both records and note the conflict instead of silently overwriting.

## Analysis order

1. Read `profile.json` for goal, constraints, schedule, and equipment.
2. Read recent `training-history.json` entries for completed work.
3. Read `body-metrics-history.json` when body composition matters.
4. Read `nutrition-history.json` when the user asks about diet, cut, bulk, recomposition, adherence, or recovery.
5. Route to the goal module and recommendation decision tree.

## Output requirements

When updating saved data, say:

- Which store path was used.
- Which files were created or updated.
- How many records were imported and how many were skipped as duplicates.
- What analysis should run next.
