#!/usr/bin/env python3
# Lab 06 - K8s-SA-Token-Theft
# A pod's web app has a path-traversal (LFI) bug. Kubernetes auto-mounts the
# pod's ServiceAccount token at /var/run/secrets/kubernetes.io/serviceaccount/
# token. The SA is over-privileged (can list/read Secrets cluster-wide), so:
#   LFI -> read SA token -> hit kube-apiserver -> dump Secrets in other namespaces.
import os, base64, threading
from flask import Flask, request, Response, jsonify

HERE = os.path.dirname(os.path.abspath(__file__))
DOCROOT = os.path.join(HERE, "pod-fs", "srv", "www")   # app serves files from here
POD_TOKEN = open(os.path.join(HERE, "pod-fs", "var", "run", "secrets",
    "kubernetes.io", "serviceaccount", "token")).read().strip()

# ---- mock kube-apiserver (Bearer-token authz; SA is over-privileged) ----
api = Flask("apiserver")
SECRETS = {
    ("default", "app-config"): {"DB_URL": "postgres://app:app@db/app"},
    ("kube-system", "cloud-credentials"): {
        "aws_access_key_id": "AKIACLUSTERADMINKEY99",
        "aws_secret_access_key": "kubeSystemStolenSecretKeyEXAMPLE1234567890"},
}
def authed():
    return request.headers.get("Authorization", "") == f"Bearer {POD_TOKEN}"
@api.route("/api/v1/secrets")
def list_all():
    if not authed(): return _401()
    items = [{"metadata": {"namespace": ns, "name": n}} for (ns, n) in SECRETS]
    return jsonify({"kind": "SecretList", "items": items})
@api.route("/api/v1/namespaces/<ns>/secrets/<name>")
def get_secret(ns, name):
    if not authed(): return _401()
    data = SECRETS.get((ns, name))
    if not data: return Response("not found", status=404)
    enc = {k: base64.b64encode(v.encode()).decode() for k, v in data.items()}
    return jsonify({"kind": "Secret", "metadata": {"namespace": ns, "name": name}, "data": enc})
def _401():
    return Response('{"kind":"Status","code":401,"reason":"Unauthorized"}',
                    status=401, mimetype="application/json")
def run_api(): api.run(host="127.0.0.1", port=9107, threaded=True)

# ---- vulnerable pod app (path traversal / LFI) ----
app = Flask("pod-app")
@app.route("/")
def home():
    return jsonify({"app": "prod-api (in a Kubernetes pod)",
        "hint": "GET /download?file=<path> — serves files, no sanitization"})
@app.route("/download")
def download():
    f = request.args.get("file", "index.html")
    try:
        with open(os.path.join(DOCROOT, f), "rb") as fh:   # NO path sanitization
            return Response(fh.read(), mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 404
if __name__ == "__main__":
    threading.Thread(target=run_api, daemon=True).start()
    app.run(host="0.0.0.0", port=9106, threaded=True)
