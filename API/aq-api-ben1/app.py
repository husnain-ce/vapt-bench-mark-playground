#!/usr/bin/env python3
"""
Target 15. Deserial-API  -- deliberately vulnerable to INSECURE DESERIALIZATION,
a class NONE of the other 10 labs cover. A "remember me" session token is just
base64(pickle(dict)). The server pickle.loads() it with no integrity check, so a
crafted object with __reduce__ runs arbitrary code on load -> RCE.

Run:  python3 app.py      (needs Flask;  pip install flask  if missing)
"""
import base64, pickle, os
from flask import Flask, request, jsonify

app = Flask(__name__)
USERS = {"alice": "alice123"}
FLAG = "flag{pickle_deserialization_rce}"

def make_token(data: dict) -> str:
    return base64.b64encode(pickle.dumps(data)).decode()

@app.get("/")
def index():
    return jsonify(
        app="Deserial-API",
        hint="POST /login {username,password} -> session token; send it back as X-Session header to GET /whoami",
        note="the token is base64(pickle(...)) with NO signature -> forge your own object",
        flag_file="/flag.txt planted on disk; read it via the deserialization RCE")

@app.post("/login")
def login():
    d = request.get_json(force=True, silent=True) or {}
    if USERS.get(d.get("username")) == d.get("password"):
        return jsonify(session=make_token({"user": d["username"], "role": "user"}))
    return jsonify(error="bad credentials"), 401

# VULN: pickle.loads on attacker-supplied bytes -> arbitrary code execution
@app.get("/whoami")
def whoami():
    tok = request.headers.get("X-Session", "")
    try:
        data = pickle.loads(base64.b64decode(tok))     # <-- the RCE sink
    except Exception as e:
        return jsonify(error="bad session: %s" % e), 400
    return jsonify(session=data)

def _plant_flag():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "flag.txt")
    open(path, "w").write(FLAG + "\n")
    return path

if __name__ == "__main__":
    print(" * flag planted at:", _plant_flag())
    print(" * Deserial-API on http://0.0.0.0:9015")
    app.run(host="0.0.0.0", port=9015)
