#!/usr/bin/env python3
# Lab 03 - AWS-IAM-Privesc
# A minimal IAM control plane that ACTUALLY ENFORCES policy (unlike LocalStack
# Community, which does not evaluate IAM at all), so the privilege-escalation
# exploit produces a real deny -> allow flip you can see.
#
# Identity is passed via the X-Access-Key header (stands in for SigV4 signing).
# The low-priv user 'dev-ci' is attached to the customer-managed policy
# 'dev-ci-boundary', whose v1 allows iam:Get*/List* and - dangerously -
# iam:CreatePolicyVersion on that same policy. That one permission lets the
# attacker publish a NEW DEFAULT policy version granting *:*, becoming admin.
# (This is a well-known IAM privesc primitive: CreatePolicyVersion + SetAsDefault.)
import json, fnmatch
from flask import Flask, request, Response

app = Flask("iam")
ACCOUNT = "123456789012"
ACCESS_KEYS = {"AKIADEVCI0000000EXMPL": "dev-ci"}      # attacker's low-priv key
USERS = {"dev-ci": {"attached": ["arn:aws:iam::123456789012:policy/dev-ci-boundary"]}}
POLICIES = {
    "arn:aws:iam::123456789012:policy/dev-ci-boundary": {
        "PolicyName": "dev-ci-boundary", "DefaultVersionId": "v1",
        "Versions": {"v1": {"Document": {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow",
             "Action": ["iam:Get*", "iam:List*", "iam:CreatePolicyVersion",
                        "sts:GetCallerIdentity"],
             "Resource": "*"}]}}},
    },
}
ADMIN_SECRET = "crown-jewels: root account recovery code = ACME-ROOT-9c2f-EXAMPLE"

def j(obj, code=200):
    return Response(json.dumps(obj, indent=2), status=code, mimetype="application/json")
def deny(action):
    return j({"Error": {"Code": "AccessDenied",
              "Message": f"User is not authorized to perform: {action}"}}, 403)
def caller():
    return ACCESS_KEYS.get(request.headers.get("X-Access-Key", ""))
def effective_actions(user):
    acts = []
    for arn in USERS.get(user, {}).get("attached", []):
        p = POLICIES.get(arn)
        if not p:
            continue
        doc = p["Versions"][p["DefaultVersionId"]]["Document"]
        for st in doc.get("Statement", []):
            if st.get("Effect") == "Allow":
                a = st.get("Action", [])
                acts += a if isinstance(a, list) else [a]
    return acts
def allowed(user, action):
    return any(patt == "*" or fnmatch.fnmatch(action, patt)
               for patt in effective_actions(user))

@app.route("/")
def home():
    return j({"app": "IAM (enforcing) + a guarded admin resource",
              "hint": "send header  X-Access-Key: AKIADEVCI0000000EXMPL",
              "endpoints": ["/iam/whoami", "/iam/account-authorization-details",
                            "POST /iam/create-policy-version",
                            "POST /iam/attach-user-policy", "/admin/secret"]})

@app.route("/iam/whoami")
def whoami():
    u = caller()
    if not u:
        return deny("sts:GetCallerIdentity")
    return j({"User": u, "Arn": f"arn:aws:iam::{ACCOUNT}:user/{u}",
              "EffectiveActions": effective_actions(u)})

@app.route("/iam/account-authorization-details")
def gaad():
    u = caller()
    if not u or not allowed(u, "iam:GetAccountAuthorizationDetails"):
        return deny("iam:GetAccountAuthorizationDetails")
    return j({
        "UserDetailList": [{"UserName": un,
            "AttachedManagedPolicies": [{"PolicyArn": a} for a in USERS[un]["attached"]]}
            for un in USERS],
        "Policies": [{"Arn": arn, "DefaultVersionId": p["DefaultVersionId"],
            "PolicyVersionList": [{"VersionId": v, "Document": ver["Document"],
                "IsDefaultVersion": v == p["DefaultVersionId"]}
                for v, ver in p["Versions"].items()]}
            for arn, p in POLICIES.items()]})

@app.route("/iam/create-policy-version", methods=["POST"])
def create_pv():
    u = caller()
    if not u or not allowed(u, "iam:CreatePolicyVersion"):
        return deny("iam:CreatePolicyVersion")
    body = request.get_json(force=True, silent=True) or {}
    arn, doc = body.get("PolicyArn"), body.get("PolicyDocument")
    setdef = bool(body.get("SetAsDefault", False))
    p = POLICIES.get(arn)
    if not p:
        return j({"Error": {"Code": "NoSuchEntity"}}, 404)
    vid = "v%d" % (len(p["Versions"]) + 1)
    p["Versions"][vid] = {"Document": doc}
    if setdef:
        p["DefaultVersionId"] = vid
    return j({"PolicyVersion": {"VersionId": vid, "IsDefaultVersion": setdef}})

@app.route("/iam/attach-user-policy", methods=["POST"])
def attach():
    u = caller()
    if not u or not allowed(u, "iam:AttachUserPolicy"):
        return deny("iam:AttachUserPolicy")
    body = request.get_json(force=True, silent=True) or {}
    USERS.setdefault(body.get("UserName"), {"attached": []})["attached"].append(
        body.get("PolicyArn"))
    return j({"ok": True})

@app.route("/admin/secret")
def admin_secret():
    u = caller()
    if not u or not allowed(u, "secretsmanager:GetSecretValue"):
        return deny("secretsmanager:GetSecretValue")
    return j({"SecretString": ADMIN_SECRET})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9133, threaded=True)
