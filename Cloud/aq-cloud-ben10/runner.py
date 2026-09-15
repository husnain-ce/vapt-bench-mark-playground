#!/usr/bin/env python3
# Lab 10 - CICD-Pipeline-Secret-Leak
# A minimal GitHub-Actions-style runner that demonstrates two real CI/CD flaws
# in .github/workflows/ci.yml:
#   1) pull_request_target -> the workflow runs WITH repo secrets even for
#      untrusted fork PRs (and checks out the attacker's head SHA).
#   2) Script injection: the attacker-controlled expression
#      ${{ github.event.pull_request.title }} is interpolated straight into a
#      shell `run:` step, so a crafted PR title runs arbitrary commands with the
#      secrets present in the environment.
#
# Usage: python3 runner.py .github/workflows/ci.yml <event.json>
import sys, json, os, re, subprocess, yaml

def resolve_env(env_map, secrets):
    out = {}
    for k, v in (env_map or {}).items():
        s = str(v).strip()
        m = re.fullmatch(r"\$\{\{\s*secrets\.([A-Za-z0-9_]+)\s*\}\}", s)
        out[k] = secrets.get(m.group(1), "") if m else s
    return out

def expand_event(script, event):
    # GitHub expands ${{ github.event.* }} into the script text BEFORE bash runs it.
    def repl(m):
        cur = event
        for p in m.group(1).split(".")[2:]:      # drop 'github','event'
            cur = cur.get(p, "") if isinstance(cur, dict) else ""
        return str(cur)
    return re.sub(r"\$\{\{\s*(github\.event\.[^}]+?)\s*\}\}", repl, script)

def main():
    if len(sys.argv) != 3:
        print("usage: runner.py <workflow.yml> <event.json>"); sys.exit(2)
    wf, ev = sys.argv[1], sys.argv[2]
    lab_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(wf))))
    secrets = {}
    sp = os.path.join(lab_root, "secrets.json")
    if os.path.exists(sp):
        secrets = json.load(open(sp))
    event = json.load(open(ev))
    doc = yaml.safe_load(open(wf))
    trig = doc.get("on", doc.get(True))          # PyYAML parses bare 'on:' as True
    print(f"[runner] trigger: {list(trig) if isinstance(trig, dict) else trig}")
    for jname, job in doc.get("jobs", {}).items():
        print(f"[runner] job: {jname}")
        for step in job.get("steps", []):
            name = step.get("name", step.get("uses", "step"))
            if "run" not in step:
                print(f"  - step '{name}': action {step.get('uses')} "
                      f"(would checkout ref={step.get('with', {}).get('ref')})")
                continue
            env = dict(os.environ)
            env.update(resolve_env(step.get("env"), secrets))
            script = expand_event(step["run"], event)
            print(f"  - step '{name}': executing expanded script:")
            print("    | " + script.rstrip("\n").replace("\n", "\n    | "))
            r = subprocess.run(["bash", "-c", script], cwd=lab_root, env=env,
                               capture_output=True, text=True)
            for line in r.stdout.splitlines(): print("      " + line)
            for line in r.stderr.splitlines(): print("      [stderr] " + line)

if __name__ == "__main__":
    main()
