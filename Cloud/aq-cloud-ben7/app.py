#!/usr/bin/env python3
# Lab 07 - K8s-Kubelet-Exposed
# The kubelet read/write API (normally :10250) is running with anonymous auth
# enabled (--anonymous-auth=true / authorization-mode=AlwaysAllow). Anyone who
# can reach it can enumerate pods AND exec commands inside containers:
#   GET /pods  ->  POST /run/{ns}/{pod}/{container} with cmd=  ->  RCE-in-pod.
from flask import Flask, request, Response, jsonify

app = Flask("kubelet")

PODS = {"kind": "PodList", "items": [{
    "metadata": {"name": "prod-api", "namespace": "default"},
    "spec": {"containers": [{"name": "app", "image": "acme/prod-api:1.4",
        "env": [{"name": "AWS_ACCESS_KEY_ID", "value": "AKIAPODENVEXAMPLE01"},
                {"name": "AWS_SECRET_ACCESS_KEY", "value": "podEnvSecretKeyEXAMPLEabcdef0123456789"}]}]},
    "status": {"phase": "Running", "podIP": "10.1.2.3"}}]}

SA_TOKEN = ("eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6"
            "ZGVmYXVsdDpwcm9kLWFwaS1zYSJ9.KUBELET_EXEC_STOLEN_TOKEN")

def sim_exec(cmd):
    c = cmd.strip()
    if c == "id":
        return "uid=0(root) gid=0(root) groups=0(root)\n"
    if c == "env":
        return ("AWS_ACCESS_KEY_ID=AKIAPODENVEXAMPLE01\n"
                "AWS_SECRET_ACCESS_KEY=podEnvSecretKeyEXAMPLEabcdef0123456789\n"
                "DB_PASSWORD=prod-pod-db-pw\nHOSTNAME=prod-api\n")
    if c.startswith("cat ") and "serviceaccount/token" in c:
        return SA_TOKEN + "\n"
    if c == "ls /" or c == "ls":
        return "app\nbin\netc\nvar\nrun\n"
    return f"(simulated) executed: {c}\n"

@app.route("/pods")
def pods():
    return jsonify(PODS)
@app.route("/run/<ns>/<pod>/<container>", methods=["POST"])
def run(ns, pod, container):
    cmd = request.form.get("cmd", request.args.get("cmd", ""))
    return Response(sim_exec(cmd), mimetype="text/plain")
@app.route("/")
def home():
    return jsonify({"app": "kubelet (anonymous-auth ENABLED)",
        "endpoints": ["GET /pods", "POST /run/{ns}/{pod}/{container}  cmd=<shell>"]})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9108, threaded=True)
