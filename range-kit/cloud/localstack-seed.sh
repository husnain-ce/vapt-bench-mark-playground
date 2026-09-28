#!/usr/bin/env bash
# Seed LocalStack with deliberately-misconfigured AWS resources for the Aqira Cyber Range.
# All emulated (LocalStack) — no real AWS account, no spend. Loopback only.
set -uo pipefail
export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1
# Path-independent: prefer the kit venv, fall back to awslocal on PATH.
_SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AWSLOCAL="${AWSLOCAL:-$_SELF_DIR/../.venv/bin/awslocal}"
[ -x "$AWSLOCAL" ] || AWSLOCAL="$(command -v awslocal || echo awslocal)"
BUCKET="aqira-public-loot"

echo "### [1] Create a PUBLIC S3 bucket with sensitive objects"
$AWSLOCAL s3 mb "s3://$BUCKET"
# Disable the account/bucket public-access-block so a public policy can take effect
$AWSLOCAL s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

# Sensitive loot objects
printf 'AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\nAWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nDB_PASSWORD=SuperS3cretDbP@ss\n' > /tmp/ls_credentials.env
printf '{"customers":[{"name":"Alice","ssn":"111-22-3333","cc":"4111111111111111"},{"name":"Bob","ssn":"444-55-6666"}]}\n' > /tmp/ls_customers.json
$AWSLOCAL s3 cp /tmp/ls_credentials.env "s3://$BUCKET/credentials.env"
$AWSLOCAL s3 cp /tmp/ls_customers.json "s3://$BUCKET/customer-pii.json"

# Public-read bucket policy (anyone can GetObject / ListBucket) -- the misconfig
cat > /tmp/ls_public_policy.json <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadEverything",
      "Effect": "Allow",
      "Principal": "*",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::$BUCKET", "arn:aws:s3:::$BUCKET/*"]
    }
  ]
}
JSON
$AWSLOCAL s3api put-bucket-policy --bucket "$BUCKET" --policy file:///tmp/ls_public_policy.json
# Also mark objects public-read via ACL
$AWSLOCAL s3api put-object-acl --bucket "$BUCKET" --key credentials.env --acl public-read 2>/dev/null || true

echo "### [2] Over-permissive IAM policy (Action:* Resource:* -> full admin)"
cat > /tmp/ls_admin_policy.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "*", "Resource": "*" }
  ]
}
JSON
$AWSLOCAL iam create-user --user-name range-dev
$AWSLOCAL iam create-policy --policy-name AllowEverything --policy-document file:///tmp/ls_admin_policy.json
$AWSLOCAL iam attach-user-policy --user-name range-dev \
  --policy-arn arn:aws:iam::000000000000:policy/AllowEverything
# Access keys for that over-privileged user
$AWSLOCAL iam create-access-key --user-name range-dev > /tmp/ls_range_dev_keys.json

echo "### [3] Plaintext secret in Secrets Manager"
$AWSLOCAL secretsmanager create-secret --name prod/db/master \
  --secret-string '{"username":"admin","password":"pr0d-Db-M@ster-2026"}' 2>/dev/null || true

echo "### SEED COMPLETE"
