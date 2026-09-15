#!/usr/bin/env python3
# Lab 09 - GCP-Metadata-SSRF
# SSRF on a GCE instance. GCP metadata (metadata.google.internal) requires the
# header "Metadata-Flavor: Google". The default service-account token endpoint
# mints an OAuth token. SSRF -> SA token -> read a Secret Manager secret from
# the (token-protected) API.
import json, threading, http.client, base64
from urllib.parse import urlparse
from flask import Flask, request, Response, jsonify

MD_HOST, MD_PORT = "127.0.0.1", 9121              # metadata.google.internal, internal only
SA_TOKEN = "ya29.a0AfB_byC-GCP-SERVICE-ACCOUNT-OAUTH-TOKEN-EXAMPLE"

# ---- mock GCP metadata (needs 'Metadata-Flavor: Google') ----
md = Flask("gcp-md")
def bad_flavor():
    return request.headers.get("Metadata-Flavor", "") != "Google"
@md.route("/computeMetadata/v1/project/project-id")
def project():
    if bad_flavor(): return Response("Missing Metadata-Flavor:Google header", status=403)
    return Response("acme-prod-1234", mimetype="text/plain")
@md.route("/computeMetadata/v1/instance/service-accounts/default/email")
def sa_email():
    if bad_flavor(): return Response("Missing Metadata-Flavor:Google header", status=403)
    return Response("prod-runtime@acme-prod-1234.iam.gserviceaccount.com", mimetype="text/plain")
@md.route("/computeMetadata/v1/instance/service-accounts/default/token")
def sa_token():
    if bad_flavor(): return Response("Missing Metadata-Flavor:Google header", status=403)
    return jsonify({"access_token": SA_TOKEN, "expires_in": 3599, "token_type": "Bearer"})
def run_md(): md.run(host=MD_HOST, port=MD_PORT, threaded=True)

# ---- mock Secret Manager (token-protected, internet-facing on 9122) ----
sm = Flask("secretmgr")
DB_PASS = "GCP-Prod-DB-Sup3rSecret!"
@sm.route("/v1/projects/<proj>/secrets/<name>/versions/latest:access")
def access(proj, name):
    if request.headers.get("Authorization", "") != f"Bearer {SA_TOKEN}":
        return Response(json.dumps({"error": {"code": 401, "status": "UNAUTHENTICATED"}}),
                        status=401, mimetype="application/json")
    return jsonify({"name": f"projects/{proj}/secrets/{name}/versions/1",
        "payload": {"data": base64.b64encode(DB_PASS.encode()).decode()}})
def run_sm(): sm.run(host="0.0.0.0", port=9122, threaded=True)

# ---- vulnerable app (SSRF sink) ----
app = Flask("app")
RESOLVE = {"metadata.google.internal": (MD_HOST, MD_PORT), "169.254.169.254": (MD_HOST, MD_PORT)}
def ssrf_fetch(url, extra, timeout=4):
    u = urlparse(url); host = u.hostname; port = u.port or (443 if u.scheme == "https" else 80)
    ip, rport = RESOLVE.get(host, (host, port))
    path = u.path or "/"
    if u.query: path += "?" + u.query
    hdrs = {"Host": host}; hdrs.update(extra)
    conn = http.client.HTTPConnection(ip, rport, timeout=timeout)
    conn.request("GET", path, headers=hdrs)
    r = conn.getresponse(); body = r.read().decode("utf-8", "replace"); conn.close()
    return r.status, body
@app.route("/")
def home():
    return jsonify({"app": "Link Unfurler (runs on GCE w/ a service account)",
        "hint": "GET /fetch?url=<url>&hdr=Name:Value  (hdr repeatable)"})
@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    if not url: return jsonify({"error": "pass ?url="}), 400
    extra = {}
    for h in request.args.getlist("hdr"):
        if ":" in h:
            k, v = h.split(":", 1); extra[k.strip()] = v.strip()
    try:
        s, b = ssrf_fetch(url, extra); return Response(b, status=s, mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e)}), 502
if __name__ == "__main__":
    threading.Thread(target=run_md, daemon=True).start()
    threading.Thread(target=run_sm, daemon=True).start()
    app.run(host="0.0.0.0", port=9120, threaded=True)
