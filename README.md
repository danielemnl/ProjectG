# Project G pipeline (everything up to 1 Nov)

Tested offline with `python selftest.py` (toy verifier cases + synthetic scores → AUROC/catch-rate/figures). NOT yet run on real data.

## Run order
| # | Where | Command | Output |
|---|---|---|---|
| 0 | Internet notebook | `pip install evalplus; python prepare_problems.py` | problems.jsonl |
| 1 | Internet notebook | `export ATTACKER_BASE_URL=… ATTACKER_API_KEY=… ATTACKER_MODEL=…`<br>`python generate.py --problems problems.jsonl --out solutions.jsonl --kinds honest backdoor --limit 50` (pilot), then drop `--limit` | solutions.jsonl (resumable) |
| 2 | **Offline** Kaggle notebook (Internet OFF, no Secrets/Drive) | `python verify.py --problems problems.jsonl --solutions solutions.jsonl --out verified.jsonl` | verified.jsonl |
| 3 | GPU notebook, once per model | `python monitor.py --model Qwen/Qwen2.5-Coder-{0.5B,1.5B,3B,7B}-Instruct --verified verified.jsonl --out scores.jsonl` | scores.jsonl |
| 4 | Anywhere | `python analyze.py --scores scores.jsonl --outdir results` | results.csv, fig1–3 |

Upload the .py files with the datasets in steps 2–3. Add decoys later with `--kinds honest backdoor decoy`, ablations with `--variants direct_prob cot_prob direct_noprob cot_noprob`.

## Checks before trusting numbers
1. Pilot: after 50 problems, check verified-backdoor rate (<20% → fallbacks in the brief). Read ~10 backdoors by eye.
2. `n_visible=3` assumes the first 3 EvalPlus base inputs are the original MBPP tests — confirm on one problem.
3. Pre-registration (`prereg.md`): fill in attacker name, commit before step 3.
4. Time the 7B at 1 batch, then extrapolate before launching all variants.
5. If `reason` shows many `banned_import_or_call`, stop and tell the instructor (brief's safety rule).
6. Verbalized = argmax over digit logits (constrained, so no parse failures); say so in Methods.

## Status vs. schedule (26 Oct–1 Nov: full generation, verification, all monitors base variant)
Done here: all code, prereg draft, selftest. Needs you (I have no internet/GPU/API keys): steps 0–4 above.
