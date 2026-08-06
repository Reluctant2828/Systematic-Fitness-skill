# Xunji / 训记 Integration

Use this reference only when the user asks to read, import, summarize, or write back Xunji/训记 records. It describes the safety contract; it is not a replacement for an authenticated local helper or the user's current API schema.

## Access boundary

- Keep credentials in a local secret store or approved environment variable. Never put keys in the skill package, logs, prompts, saved JSON, or the answer.
- Reading is read-only and may use the user's current helper or API contract. If no usable helper, endpoint, request body, or authorization is available, ask for the missing contract instead of guessing.
- Do not claim that a record was read or written unless the request returned a parseable payload and the relevant fields were verified.

## Known endpoint shape

The previously supplied Xunji contract uses:

- Read: `POST https://trains.xunjiapp.cn/api_trains_for_llm_v2`
- Write: `POST https://trains.xunjiapp.cn/api_upsert_trains_for_llm_v2`

Use the current user-provided request schema for authentication and body fields. Do not invent headers, field names, or a success envelope from these URLs alone.

## Read protocol

1. Resolve the requested date range and whether the user needs summaries or full records. Default to `include_full_data: false` when that field exists.
2. Cache the same `datestr` read for no more than 90 seconds. Force-refresh when the user says a record was completed, corrected, or asks to inspect the latest server state.
3. Accept a legal response whose payload is in top-level `res` even when `success` is absent. Validate the actual record list before analysis.
4. Classify every returned training item as `completed`, `planned`, `skipped`, or `unknown` from the server's completion fields and the user's explicit correction.
5. For "练完了", "自己去看", or a correction to a planned record, refresh first and prefer the confirmed completed record over the stale plan.

Only completed records advance a rolling PPL or other slot pointer. A skipped session is rest and keeps the next slot unchanged.

## Write protocol

Write-back is a separate authorization step, even when the user authorized a read.

1. Validate locally before network access: dates, exercise names, sets, reps, loads, status, `localid`, and the user's equipment constraints.
2. Show a concise field-level change summary: date, session, records added/updated, preserved identifiers, and any unresolved exercise names.
3. Wait for explicit confirmation in the current conversation unless the user has already given an unambiguous write instruction that includes the target records and action.
4. Commit once. Keep the endpoint's existing `localid`, `start`, `end`, and `done` fields when updating an existing record; keep unfinished groups as `done: false`.
5. Respect the supplied limits: at most 4 simultaneous training records, 15 exercises per record, and 20 sets per exercise unless the current API contract says otherwise.
6. Re-read the affected date range after a successful response and compare the normalized result with the intended change.

Do not use a server-side "dry run" as the safety gate unless the endpoint is proven non-persistent. A prior contract allowed dry-run-shaped requests to persist duplicate records.

## Failure recovery

- Timeout, SSL EOF, connection reset, or a closed client stream does not prove that the write failed. Re-read the affected date range before retrying.
- If the re-read shows the intended record, stop; do not duplicate it. If it shows a partial write, report the difference and ask before repairing it.
- Keep per-operation evidence only in a user-approved audit path or the current conversation, without credentials: timestamp, date range, action, response status, record counts, source freshness, and verification result.

## Output minimum

For a read, report date range, number of completed/planned/skipped/unknown records, source freshness, and the exact completed record used for the decision. For a write, additionally report the confirmation, change summary, post-write parity, and any unresolved or skipped items.
