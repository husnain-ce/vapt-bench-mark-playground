#!/usr/bin/env python3
# Lab 08 - Azure-IMDS-Managed-Identity
# SSRF on an Azure VM. Azure IMDS (169.254.169.254) requires header
# "Metadata: true". Its identity endpoint mints a managed-identity access token
# for a requested resource (here Key Vault). SSRF -> token -> read Key Vault
# secret from the (token-protected) vault endpoint.
import json, threading, http.client
from urllib.parse import urlparse
from flask import Flask, request, Response, jsonify

IMDS_HOST, IMDS_PORT = "127.0.0.1", 9111          # link-local, internal only
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1Ni...MANAGED-IDENTITY-TOKEN"

# ---- mock Azure IMDS (needs 'Metadata: true') ----
imds = Flask("azure-imds")
def bad_meta():
    return request.headers.get("Metadata", "").lower() != "true"
@imds.route("/metadata/instance")
def instance():
    if bad_meta(): return Response("Required metadata header not specified", status=400)
    return jsonify({"compute": {"name": "prod-vm-01", "resourceGroupName": "prod-rg",
        "subscriptionId": "00000000-0000-0000-0000-000000000000"}})
@imds.route("/metadata/identity/oauth2/token")
def token():
    if bad_meta(): return Response("Required metadata header not specified", status=400)
    res = request.args.get("resource", "")
    return jsonify({"access_token": ACCESS_TOKEN, "resource": res,
        "token_type": "Bearer", "expires_in": "3599", "client_id":
        "11111111-2222-3333-4444-555555555555"})
def run_imds(): imds.run(host=IMDS_HOST, port=IMDS_PORT, threaded=True)

# ---- mock Azure Key Vault (token-protected, internet-facing on 9112) ----
vault = Flask("keyvault")
SECRET = {"value": "Server=prod-sql;Database=acme;User=admin;Password=Azure-Sup3r-Secret!",
          "id": "https://acme-kv.vault.azure.net/secrets/db-conn/abc123"}
@vault.route("/secrets/<name>")
def secret(name):
    if request.headers.get("Authorization", "") != f"Bearer {ACCESS_TOKEN}":
        return Response(json.dumps({"error": {"code": "Unauthorized"}}), status=401,
                        mimetype="application/json")
    return jsonify(SECRET)
def run_vault(): vault.run(host="0.0.0.0", port=9112, threaded=True)

# ---- vulnerable app (SSRF sink, forwards caller headers) ----
app = Flask("app")
RESOLVE = {"169.254.169.254": (IMDS_HOST, IMDS_PORT)}
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
    return jsonify({"app": "Image Fetcher (runs on an Azure VM w/ managed identity)",
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
    threading.Thread(target=run_imds, daemon=True).start()
    threading.Thread(target=run_vault, daemon=True).start()
    app.run(host="0.0.0.0", port=9110, threaded=True)
