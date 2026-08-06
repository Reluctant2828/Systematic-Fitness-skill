# Trigger Tests

These simulated requests were used to refine the skill's trigger boundaries.

| # | Request | Should trigger? | Reason |
|---|---|---|---|
| 1 | `/fitness 我最近训练很乱，我该怎么做？` | Yes | Explicit skill invocation plus systematic training decision. |
| 2 | `这是我四周训练截图，帮我分析哪里卡住了，怎么改增肌计划。` | Yes | Screenshot/log analysis and hypertrophy plan adjustment. |
| 3 | `我每周只能练三天，目标减脂塑形，帮我重新排训练。` | Yes | Goal, schedule constraint, and program design. |
| 4 | `100g 鸡胸肉多少热量？` | No | Nutrition-only lookup without a training programming decision. |
| 5 | `帮我画一个健身房宣传海报。` | No | Creative/design task unrelated to training analysis. |
| 6 | `我想用北欧腿弯举，但动作库里没有，怎么安排？` | Yes | Exercise substitution and outside-library fallback are training-program decisions. |
| 7 | `我想增肌，胸和背一周练多少组比较合适？` | Yes | Routes to `goal-hypertrophy.md`. |
| 8 | `我在减脂期，怎么改训练才能保住力量和肌肉？` | Yes | Routes to `goal-fat-loss-recomposition.md`. |
| 9 | `我肩太弱，想做一个 6 周肩部专攻。` | Yes | Routes to `goal-specialization.md`. |
| 10 | `我想把深蹲卧推硬拉做一个力量举周期。` | Yes | Routes to `goal-powerlifting.md`. |
| 11 | `站姿器械侧平举 35kg 做满了，下次能不能直接 40kg？` | Yes | Must apply long-lever shoulder isolation progression constraints. |
| 12 | `这个动作算法不好算，能不能直接换掉？` | Yes | Must not avoid exercises just because progression is hard to calculate. |
| 13 | `增肌到底该二分化、三分化、四分化还是五分化？` | Yes | Routes to `goal-hypertrophy.md` plus `hypertrophy-splits.md`. |
| 14 | `三分化推力日怎么安排？卧推、上斜、臂屈伸、侧平举分别怎么递进？` | Yes | Routes to `goal-hypertrophy.md`, `hypertrophy-splits.md`, and `ppl-practical.md`. |
| 15 | `我想照着高水平选手的背部训练，只做很少正式组但强度拉满，可以吗？` | Yes | Routes to `ppl-practical.md` for low-volume high-intensity and execution-control rules. |
| 16 | `我每周只能练 4 到 5 天，三分化怎么滚动安排？` | Yes | Routes to `ppl-practical.md` for rolling 三分化 templates. |
| 17 | `我胸弱，PPL 里能不能插一个胸专项日？` | Yes | Routes to `ppl-practical.md` for specialization insertion rules. |
| 18 | `我每周练 4 天，二分化上肢 A/B 下肢 A/B 怎么排？` | Yes | Routes to `split-two-division.md` for Upper/Lower A/B structure. |
| 19 | `四分化是胸背腿肩手臂好，还是上下肢 A/B 好？` | Yes | Routes to `split-four-division.md` for default four-day split selection. |
| 20 | `我想五分化，胸背腿肩手臂一天一个部位可以吗？` | Yes | Routes to `split-five-division.md` for readiness, secondary stimulus, and weak-point rules. |
| 21 | `我减脂两周体重不动，是不是平台？有氧和步数怎么调？` | Yes | Routes to `fat-loss-recomposition-advanced.md` for plateau, NEAT, and cardio rules. |
| 22 | `我肩中束没感觉，想做 6 周肩部专攻。` | Yes | Routes to `specialization-advanced.md` for weak-point diagnosis and shoulder specialization. |
| 23 | `我卧推卡锁定，想做 12 周力量举周期。` | Yes | Routes to `powerlifting-advanced.md` for bench sticking point and SBD periodization. |
| 24 | `这是我的初始数据：男，175cm，78kg，新手，每周 4 天，健身房器械齐，帮我安排。` | Yes | Routes to `user-profile-intake.md` before goal modules. |
| 25 | `这是我最近 6 周训练记录，帮我分析到底该加量还是减量。` | Yes | Routes to `training-log-analysis.md` and `recommendation-decision-tree.md`. |
| 26 | `我这 30 天体重、腰围和照片变化在这里，是不是减脂没效果？` | Yes | Routes to `body-metrics-analysis.md` and fat-loss module. |
| 27 | `我计划基本能练完，但胸没进步、睡眠还行，这次应该只改哪里？` | Yes | Routes to `recommendation-decision-tree.md` for smallest useful change. |
| 28 | `这里有一个训练日志 CSV，帮我汇总每周各肌群训练量和动作趋势。` | Yes | Runs `scripts/summarize_training_logs.py`, then routes to `training-log-analysis.md`. |
| 29 | `帮我建立长期用户档案，并把这份训练 CSV 保存进去。` | Yes | Routes to `user-data-management.md` and uses `scripts/manage_user_data.py` when file writes are approved. |
| 30 | `这是我最近两周饮食记录和体重变化，帮我看减脂是不是吃太少。` | Yes | Routes to `nutrition-log-analysis.md`, `body-metrics-analysis.md`, and fat-loss module. |
| 31 | `这是训练导出：两条已完成、一条计划、一条跳过，帮我判断下次 PPL 练什么。` | Yes | Keep record states separate; only completed work advances progression and the rolling slot. |
| 32 | `练完了，自己去看训记服务器记录并更新今天的训练。` | Yes | Read Xunji with a force refresh, verify the completed record, then show a write summary before any write-back. |
| 33 | `把这份 CSV 导入长期档案，导入前备份原文件。` | Yes | Use `manage_user_data.py --backup`, report target path and added/skipped/rejected counts, preserve status/provenance, and reject secret-like fields before writing. |
| 34 | `我做卧推时胸口痛并且头晕，还能继续练吗？` | Yes | Safety-only route; tell the user to stop the provoking activity and seek urgent qualified help without diagnosing. |
| 35 | `这份表只有 planned 和 skipped，没有 completed，帮我安排下一次。` | Yes | Do not progress from it; state that no completed comparison exists and ask only for the minimum missing evidence or give a conservative start. |
| 36 | `我想加量，帮我改一下。` | No | Generic phrase without training context should not trigger the specialized skill. |
| 37 | `My bench has stalled for four completed sessions. Decide whether to add volume or deload.` | Yes | English trigger; route to log review and decision tree, then report the canonical bottleneck and smallest change. |
| 38 | `Read my Xunji record for today, but do not write anything.` | Yes | API read-only profile; force-refresh when freshness matters, report source/counts, and perform no write-back. |
| 39 | `我肩中束弱，动作库里有多个同名哑铃飞鸟，帮我选一个。` | Yes | Exercise-choice profile; report `ambiguous_exact`, candidate names, and ask for the body-part/equipment confirmation. |

Refinement from tests: the description explicitly includes `/fitness`, `$system-fitness-advisor`, Xunji/API, CSV/JSON training data, screenshots, and the four program domains, while excluding medical diagnosis, nutrition-only lookup, and non-training creative requests. Record state is part of the trigger contract: planned, skipped, and unknown entries must not be treated as completed. If another installed skill also claims `/fitness`, keep only one active `/fitness` skill or use `$system-fitness-advisor` for explicit routing.

## Final acceptance smoke tests

Run these acceptance requests mentally before installing or merging the skill:

| # | Request | Expected routing | Expected behavior |
|---|---|---|---|
| A | `/fitness 这是我的初始数据：男，175cm，78kg，新手，每周 4 天，器械齐，目标增肌，帮我安排。` | Trigger; `user-profile-intake.md`, `goal-hypertrophy.md`, `hypertrophy-splits.md` | Ask only missing high-impact questions if needed, choose a split, and output a concrete first block. |
| B | `这是我最近 6 周训练 CSV，帮我看该加量、减量还是 deload。` | Trigger; run `scripts/summarize_training_logs.py`, then `training-log-analysis.md` and `recommendation-decision-tree.md` | Use completed logs as evidence, name the bottleneck, and recommend the smallest useful change. |
| C | `我减脂两周体重没动，训练还掉力量，步数和有氧怎么调？` | Trigger; `body-metrics-analysis.md`, `goal-fat-loss-recomposition.md`, `fat-loss-recomposition-advanced.md` | Separate fat-loss plateau from fatigue, preserve key lifts, and adjust deficit/cardio/NEAT conservatively. |
| D | `我肩中束弱，站姿器械侧平举 35kg 做满了，下次能不能直接 40kg？` | Trigger; `goal-specialization.md`, `specialization-advanced.md`, shared load rules | Reject blind 35kg to 40kg+ jumps; prefer reps, control, density, or target-specific shoulder block. |
| E | `100g 鸡胸肉多少热量？` | Do not trigger | Treat as nutrition-only lookup unless the user asks for a training decision. |
| F | `把这份训练记录和饮食记录都导入我的长期档案，然后总结最近一周训练和蛋白质。` | Trigger; `user-data-management.md`, `training-log-analysis.md`, `nutrition-log-analysis.md` | Save or update the user-approved data store, deduplicate imports, then summarize training and nutrition evidence. |
| G | `这是训练 CSV，里面有 planned、completed、skipped 三种状态。` | Trigger; `training-log-analysis.md`, `recommendation-decision-tree.md` | Exclude planned/skipped rows from completed-work trends and state the counts and confidence. |
| H | `我做卧推时胸口痛并且头晕，还能继续练吗？` | Trigger; safety gate only | Stop normal programming, avoid diagnosis, and direct the user to urgent qualified evaluation. |
| I | `这份表只有 planned 和 skipped，没有 completed，帮我安排下一次。` | Trigger; `training-log-analysis.md`, `recommendation-decision-tree.md` | Do not invent progression; use a conservative start or ask the smallest high-impact question. |
| J | `我想加量，帮我改一下。` | Do not trigger | Ask for context outside this specialized skill; do not treat a generic phrase as a training request. |
| K | `Read my Xunji record for today, but do not write anything.` | Trigger; `xunji-integration.md` | Use read-only API profile, preserve the no-write instruction, and report freshness/record state. |

Acceptance result after the latest polish: A-D, F-I, and K should trigger the skill; E and J should not. Ambiguous exercise names must use the canonical match schema and be reported under `unresolved_exercises` instead of silently forced into a library match.
