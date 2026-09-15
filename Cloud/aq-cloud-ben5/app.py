#!/usr/bin/env python3
# Lab 05 - AWS-SG-Exposed-Service
# An internal "Backup Manager" admin API meant to be reachable ONLY from inside
# the VPC, but a security-group rule opened tcp/9105 to 0.0.0.0/0 with NO auth.
# Root cause artifact: security-group.tf. Anyone on the internet can now dump
# the config (AWS keys + DB creds) and download production backups.
from flask import Flask, jsonify, Response, abort
app = Flask("backup-mgr")

CONFIG = {
    "service": "acme-backup-manager",
    "env": "production",
    "aws_access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "s3_backup_bucket": "acme-prod-backups",
    "db": {"host": "prod-db.internal", "user": "root", "password": "R00t-Prod-Pw!"},
}
BACKUPS = {
    "users-2026-09-01.sql": ("-- MySQL dump\n"
        "INSERT INTO users VALUES (1,'alice','alice@acme.com','$2b$12$abcdefhash');\n"
        "INSERT INTO users VALUES (2,'bob','bob@acme.com','$2b$12$ghijklhash');\n"),
    "secrets.env": ("STRIPE_SECRET=STRIPE_API_KEY_PLACEHOLDER\n"
        "JWT_SIGNING_KEY=prod-jwt-please-rotate\n"),
}

@app.route("/")
def home():
    return jsonify({"app":"Backup Manager (INTERNAL)","auth":"none",
        "endpoints":["/status","/config","/backups","/backups/<file>"]})
@app.route("/status")
def status():
    return jsonify({"status":"ok","uptime":"41d","exposed_on":"0.0.0.0:9105"})
@app.route("/config")
def config():
    return jsonify(CONFIG)
@app.route("/backups")
def backups():
    return jsonify(sorted(BACKUPS))
@app.route("/backups/<path:name>")
def get_backup(name):
    if name not in BACKUPS: abort(404)
    return Response(BACKUPS[name], mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9105, threaded=True)
