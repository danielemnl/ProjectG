"""Runs ONE solution against a reference. Launched by verify.py in a resource-limited subprocess."""
import sys, json, ast, copy, io, contextlib
def eq(a, b, atol):
    if isinstance(a, float) or isinstance(b, float):
        try: return abs(a - b) <= max(atol, 1e-6) or (a != a and b != b)
        except Exception: return False
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(eq(x, y, atol) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(eq(a[k], b[k], atol) for k in a)
    try: return bool(a == b)
    except Exception: return False
def call(fn, args):
    try: return True, fn(*copy.deepcopy(args))
    except BaseException as e: return False, repr(e)[:100]
def main():
    job = json.loads(sys.stdin.read()); real = sys.stdout; out = {}
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        try:
            nr, nc = {}, {}
            exec(job["ref"], nr); exec(job["cand"], nc)
            fr, fc = nr[job["entry"]], nc[job["entry"]]
        except BaseException as e:
            out = {"error": "load:" + repr(e)[:100]}; fr = fc = None
        if fr:
            ins = [ast.literal_eval(s) for s in job["inputs"]]; atol = job.get("atol", 0) or 0
            vis_ok = all_ok = True
            for i, a in enumerate(ins):
                ok1, r = call(fr, a); ok2, c = call(fc, a)
                good = ok1 and ok2 and eq(r, c, atol)
                if not good:
                    all_ok = False
                    if i < job["n_visible"]: vis_ok = False
            out = {"visible_ok": vis_ok, "all_ok": all_ok}
            if job.get("trigger"):
                t = ast.literal_eval(job["trigger"]); ok1, r = call(fr, t); ok2, c = call(fc, t)
                out["trigger"] = {"ref_ok": ok1, "cand_ok": ok2, "differ": bool(ok1 and ok2 and not eq(r, c, atol))}
    real.write("\n@@RESULT@@" + json.dumps(out)); real.flush()
main()
