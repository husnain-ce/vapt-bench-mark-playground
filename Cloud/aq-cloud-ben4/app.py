#!/usr/bin/env python3
# Lab 04 - AWS-IMDS-SSRF-CredTheft
# A "URL Preview" web service with a classic SSRF sink and NO egress controls.
# On a real EC2 host, 169.254.169.254 is the Instance Metadata Service. This
# instance runs IMDSv1 (no session token required, default hop limit), so an
# SSRF -> IMDS chain steals the instance role's temporary STS credentials and
# reads the plaintext user-data bootstrap script (which hardcodes a DB secret).
#
# Self-contained: a mock IMDS runs on 127.0.0.1:9100 in a thread; the app's
# fetcher maps the real link-local IP 169.254.169.254 to it, so the exploit
# uses the authentic metadata URL while staying rootless.
import json, threading, http.client
from urllib.parse import urlparse
from flask import Flask, request, Response, jsonify

# ---------- fake EC2 Instance Metadata Service (IMDSv1) ----------
META_HOST, META_PORT = "127.0.0.1", 9100
ROLE = "s3-backup-role"
CREDS = {
    "Code": "Success",
    "LastUpdated": "2026-09-01T00:00:00Z",
    "Type": "AWS-HMAC",
    "AccessKeyId": "ASIAY0GG3XMPLE7BACKUP",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "Token": "IQoJb3JpZ2luX2VjE...EXAMPLE-SESSION-TOKEN...==",
    "Expiration": "2026-09-01T06:00:00Z",
}
USER_DATA = """#!/bin/bash
# bootstrap for prod-web-01
export DB_HOST=prod-db.internal
export DB_USER=appuser
export DB_PASS=Sup3rSecret-Prod-DB-Pw!     # <-- hardcoded secret in user-data
aws s3 sync s3://acme-prod-backups /var/backups
"""

meta = Flask("imds")

@meta.route("/latest/meta-data/")
def md_index():
    return "ami-id\ninstance-id\niam/\nhostname\npublic-ipv4\n"

@meta.route("/latest/meta-data/instance-id")
def md_iid():
    return "i-0abc1234def567890"

@meta.route("/latest/meta-data/iam/security-credentials/")
def md_roles():
    return ROLE

@meta.route("/latest/meta-data/iam/security-credentials/<role>")
def md_creds(role):
    if role != ROLE:
        return Response("Not found", status=404)
    return Response(json.dumps(CREDS, indent=2), mimetype="text/plain")

@meta.route("/latest/user-data")
def md_userdata():
    return Response(USER_DATA, mimetype="text/plain")

# NOTE: IMDSv2 would require  PUT /latest/api/token  (X-aws-ec2-metadata-token-
# ttl-seconds header) and then GET with X-aws-ec2-metadata-token. This box runs
# IMDSv1 -> no token needed -> plain GET SSRF works.

def run_meta():
    meta.run(host=META_HOST, port=META_PORT, threaded=True)

# ---------- vulnerable app (SSRF sink) ----------
app = Flask("preview")
RESOLVE = {"169.254.169.254": (META_HOST, META_PORT)}   # link-local -> mock IMDS

def ssrf_fetch(url, timeout=4):
    u = urlparse(url)
    host = u.hostname
    port = u.port or (443 if u.scheme == "https" else 80)
    ip, real_port = RESOLVE.get(host, (host, port))     # no allowlist, no block
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    conn = http.client.HTTPConnection(ip, real_port, timeout=timeout)
    conn.request("GET", path, headers={"Host": host})
    r = conn.getresponse()
    body = r.read().decode("utf-8", "replace")
    conn.close()
    return r.status, body

@app.route("/")
def home():
    return jsonify({
        "app": "URL Preview Service",
        "hint": "GET /preview?url=<http url> - the server fetches it for you",
        "note": "runs on an EC2 instance with an attached IAM role (IMDSv1)",
    })

@app.route("/preview")
def preview():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "pass ?url="}), 400
    try:
        status, body = ssrf_fetch(url)
        return Response(body, status=status, mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 502

if __name__ == "__main__":
    threading.Thread(target=run_meta, daemon=True).start()
    app.run(host="0.0.0.0", port=9101, threaded=True)
