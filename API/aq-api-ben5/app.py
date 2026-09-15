#!/usr/bin/env python3
"""
Target 11. JWT-Forge-API  -- deliberately vulnerable JWT authentication service.
Focus: JWT ALGORITHM/HEADER attacks that the other 10 labs do NOT cover
       (they only ship a "weak secret"). Here the *verifier itself* is broken.

Attack surface (all reachable without knowing the real secret):
  1. alg:none          -> signature stripped, token trusted
  2. kid path traversal -> 'kid' header used as a filename to load the HMAC key
  3. jwk header inject   -> token carries its own key; server verifies against it
  4. weak HS256 secret   -> "secret123" (brute-forceable) is the fallback

Run:  python3 app.py      (needs Flask;  pip install flask  if missing)
"""
import base64, hmac, hashlib, json, os
from flask import Flask, request, jsonify

app = Flask(__name__)
WEAK_SECRET = b"secret123"                      # the real, but guessable, HMAC key
KEYDIR = os.path.join(os.path.dirname(__file__), "keys")
os.makedirs(KEYDIR, exist_ok=True)
open(os.path.join(KEYDIR, "hmac.key"), "wb").write(WEAK_SECRET)

USERS = {"alice": "alice123", "bob": "bob123"}  # ordinary, non-admin users
FLAG = "flag{jwt_alg0_c0nfusi0n_pwned}"

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def sign(header: dict, payload: dict, key: bytes) -> str:
    h = b64url(json.dumps(header, separators=(",", ":")).encode())
    p = b64url(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(key, f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{b64url(sig)}"

def issue(username, role="user"):
    return sign({"alg": "HS256", "typ": "JWT"},
                {"sub": username, "role": role}, WEAK_SECRET)

def verify(token: str):
    """INTENTIONALLY BROKEN verifier -- trusts attacker-controlled header fields."""
    try:
        h_b64, p_b64, sig_b64 = token.split(".")
    except ValueError:
        return None
    header = json.loads(b64url_dec(h_b64))
    payload = json.loads(b64url_dec(p_b64))
    alg = header.get("alg", "HS256")

    # VULN 1: 'none' algorithm accepted -> no signature required at all
    if alg.lower() == "none":
        return payload

    # pick the verification key -- from attacker-controlled header where present
    if "jwk" in header:                         # VULN 3: trust an embedded key
        key = header["jwk"].get("k", "").encode()
    elif "kid" in header:                       # VULN 2: kid used as a file path
        try:
            key = open(os.path.join(KEYDIR, header["kid"]), "rb").read()
        except OSError:
            key = b""                           # missing file -> empty key (forgeable)
    else:                                       # VULN 4: fallback weak secret
        key = WEAK_SECRET

    expected = b64url(hmac.new(key, f"{h_b64}.{p_b64}".encode(),
                               hashlib.sha256).digest())
    return payload if hmac.compare_digest(expected, sig_b64) else None

@app.get("/")
def index():
    return jsonify(app="JWT-Forge-API",
                   hint="POST /login {username,password}; GET /me; GET /admin",
                   seed_users=list(USERS))

@app.post("/login")
def login():
    d = request.get_json(force=True, silent=True) or {}
    if USERS.get(d.get("username")) == d.get("password"):
        return jsonify(token=issue(d["username"], "user"))
    return jsonify(error="bad credentials"), 401

def _claims():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return verify(auth[7:])

@app.get("/me")
def me():
    c = _claims()
    return (jsonify(c) if c else (jsonify(error="invalid token"), 401))

@app.get("/admin")
def admin():
    c = _claims()
    if not c:
        return jsonify(error="invalid token"), 401
    if c.get("role") == "admin":
        return jsonify(msg="welcome, admin", flag=FLAG)
    return jsonify(error="admins only", your_role=c.get("role")), 403

if __name__ == "__main__":
    print(" * JWT-Forge-API on http://0.0.0.0:9011   (weak secret: secret123)")
    app.run(host="0.0.0.0", port=9011)
