#!/usr/bin/env python3
# Lab 01 - AWS-S3-Public-Loot
# A faithful (minimal) S3 REST API with two misconfigured buckets:
#   acme-public-assets : anonymous ListBucket + GetObject (public read) holding
#                        sensitive objects (DB dump, credentials.json, PII CSV),
#                        plus a bucket policy whose Principal is "*".
#   acme-uploads       : anonymous PutObject (public write) -> attacker can drop
#                        arbitrary objects (defacement / malware hosting).
# Exploit with curl, or with the AWS CLI (no signing required):
#   aws --endpoint-url http://localhost:9131 --no-sign-request s3 ls s3://acme-public-assets
from flask import Flask, request, Response
app = Flask("s3")

BUCKETS = {
    "acme-public-assets": {
        "public_read": True, "public_write": False,
        "objects": {
            "config/credentials.json":
                '{"aws_access_key_id":"AKIAIOSFODNN7EXAMPLE",'
                '"aws_secret_access_key":"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"}\n',
            "backup/db-dump.sql":
                "-- prod dump\nINSERT INTO users VALUES (1,'alice','alice@acme.com');\n",
            "employees.csv":
                "name,email,ssn\nAlice,alice@acme.com,111-22-3333\nBob,bob@acme.com,444-55-6666\n",
        },
    },
    "acme-uploads": {"public_read": True, "public_write": True, "objects": {}},
}
PUBLIC_POLICY = ('{"Version":"2012-10-17","Statement":[{"Sid":"PublicRead",'
    '"Effect":"Allow","Principal":"*","Action":["s3:GetObject","s3:ListBucket"],'
    '"Resource":["arn:aws:s3:::acme-public-assets","arn:aws:s3:::acme-public-assets/*"]}]}')

def xml(body, code=200):
    return Response('<?xml version="1.0" encoding="UTF-8"?>\n' + body, status=code,
                    mimetype="application/xml")
def denied():
    return xml('<Error><Code>AccessDenied</Code><Message>Access Denied</Message></Error>', 403)

@app.route("/")
def list_buckets():
    items = "".join(f"<Bucket><Name>{b}</Name></Bucket>" for b in BUCKETS)
    return xml("<ListAllMyBucketsResult><Buckets>" + items +
               "</Buckets></ListAllMyBucketsResult>")

@app.route("/<bucket>", methods=["GET"])
@app.route("/<bucket>/", methods=["GET"])
def bucket_get(bucket):
    b = BUCKETS.get(bucket)
    if not b:
        return xml('<Error><Code>NoSuchBucket</Code></Error>', 404)
    if "policy" in request.args:      # GET /<bucket>?policy  (GetBucketPolicy)
        return Response(PUBLIC_POLICY if bucket == "acme-public-assets"
                        else '{"Statement":[]}', mimetype="application/json")
    if not b["public_read"]:
        return denied()
    contents = "".join(f"<Contents><Key>{k}</Key><Size>{len(v)}</Size></Contents>"
                       for k, v in b["objects"].items())
    return xml(f"<ListBucketResult><Name>{bucket}</Name>{contents}</ListBucketResult>")

@app.route("/<bucket>/<path:key>", methods=["GET"])
def get_object(bucket, key):
    b = BUCKETS.get(bucket)
    if not b or not b["public_read"]:
        return denied()
    if key not in b["objects"]:
        return xml('<Error><Code>NoSuchKey</Code></Error>', 404)
    return Response(b["objects"][key], mimetype="application/octet-stream")

@app.route("/<bucket>/<path:key>", methods=["PUT"])
def put_object(bucket, key):
    b = BUCKETS.get(bucket)
    if not b:
        return xml('<Error><Code>NoSuchBucket</Code></Error>', 404)
    if not b["public_write"]:         # acme-uploads allows anonymous writes
        return denied()
    b["objects"][key] = request.get_data(as_text=True)
    return Response("", status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9131, threaded=True)
