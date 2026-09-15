Cloud Lab 05. AWS-SG-Exposed-Service — Flask (Python), self-contained  ✅ (exploit verified on this box)

An internal "Backup Manager" admin API that was meant to be reachable ONLY from
inside the VPC. A security-group rule (see security-group.tf) opened tcp/9105 to
0.0.0.0/0 with NO authentication, so anyone on the internet can now read the
service config (AWS keys + DB creds) and download production database backups.

1: Get the lab:   unzip AWS-SG-Exposed-Service.zip && cd 05-AWS-SG-Exposed-Service
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9105/          <-- {"app":"Backup Manager (INTERNAL)","auth":"none",...}
   # Quick win — no auth, straight to the loot:
   curl localhost:9105/config
   #   -> {"aws_access_key_id":"AKIA...","aws_secret_access_key":"...","db":{"password":"R00t-Prod-Pw!"...}}
   curl localhost:9105/backups
   #   -> ["secrets.env","users-2026-09-01.sql"]
   curl localhost:9105/backups/secrets.env
   #   -> STRIPE_SECRET=sk_live_... / JWT_SIGNING_KEY=...
3: Stop:  Ctrl-C

Root cause artifact:  security-group.tf  (ingress cidr_blocks = ["0.0.0.0/0"] on port 9105)

Requirements:
    Python 3 + Flask                (native run — no Docker, no cloud account)
    curl

Endpoints:
    GET  /                          -> banner (auth: none)
    GET  /status                    -> uptime / exposure info
    GET  /config                    -> AWS keys + DB creds            [SECRET LEAK]
    GET  /backups                   -> list backup files
    GET  /backups/<file>            -> download a backup              [DATA EXFIL]

List of Vulnerabilities (all verified on this box):
    Over-permissive security group — 0.0.0.0/0 ingress exposes an internal-only
        admin service to the whole internet (root cause in security-group.tf).
    Missing authentication — every endpoint is reachable with no credentials.
    Sensitive data exposure — /config leaks long-lived AWS keys + DB root creds.
    Unrestricted backup download — production DB dumps and a secrets.env are
        downloadable by anyone.

Remediation: scope the SG ingress to the VPC CIDR; require auth on the service;
move backups to a private bucket; rotate the exposed keys/secrets.
