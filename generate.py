"""Attacker generation (internet notebook). Any OpenAI-compatible endpoint (Groq, Gemini-compat, ...).
env: ATTACKER_BASE_URL (e.g. https://api.groq.com/openai/v1), ATTACKER_API_KEY, ATTACKER_MODEL
usage: python generate.py --problems problems.jsonl --out solutions.jsonl --kinds honest backdoor decoy --limit 50
Resumable. Never disguises the task: prompts state the research purpose (see common.py)."""
import argparse, json, os, time, urllib.request
from common import *
def chat(prompt, temperature=0.7):
    req = urllib.request.Request(os.environ["ATTACKER_BASE_URL"].rstrip("/") + "/chat/completions",
        data=json.dumps({"model": os.environ["ATTACKER_MODEL"], "temperature": temperature, "max_tokens": 1500,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["ATTACKER_API_KEY"]})
    for wait in (2, 10, 30, 60):
        try:
            return json.load(urllib.request.urlopen(req, timeout=120))["choices"][0]["message"]["content"]
        except Exception as e:
            print("retry", repr(e)[:80]); time.sleep(wait)
    return None
ap = argparse.ArgumentParser()
ap.add_argument("--problems"); ap.add_argument("--out"); ap.add_argument("--limit", type=int, default=10**9)
ap.add_argument("--kinds", nargs="+", default=["honest", "backdoor"]); ap.add_argument("--sleep", type=float, default=2.0)
a = ap.parse_args()
probs = read_jsonl(a.problems)[:a.limit]
done = {(r["task_id"], r["kind"]) for r in read_jsonl(a.out)} if os.path.exists(a.out) else set()
for p in probs:
    for k in a.kinds:
        if (p["task_id"], k) in done: continue
        text = chat(ATTACK_PROMPTS[k].format(problem=p["prompt"]))
        if text is None: continue
        code, trig = parse_attack_reply(k, text)
        append_jsonl(a.out, {"task_id": p["task_id"], "kind": k, "code": code, "trigger_args": trig, "raw": text})
        time.sleep(a.sleep)
