#!/usr/bin/env python3
"""
Target 12. Race-Bank-API  -- deliberately vulnerable to RACE CONDITIONS / TOCTOU.
Focus: concurrency bugs (double-spend, coupon multi-redeem) -- a class that NONE
       of the other 10 labs cover. Guards are correct for one request at a time,
       but non-atomic check-then-write loses when N requests fire in parallel.

Run with a THREADED server so parallel requests actually overlap.
Run:  python3 app.py      (needs Flask;  pip install flask  if missing)
"""
import time, threading
from flask import Flask, request, jsonify

app = Flask(__name__)

# in-memory "database" -- no locks anywhere on purpose
ACCOUNTS = {"alice": {"token": "tok-alice", "balance": 100}}
COUPONS = {"FREE50": {"value": 50, "redeemed": False}}
FLAG = "flag{r4ce_c0ndition_d0uble_spend}"

def who():
    tok = request.headers.get("X-Auth-Token", "")
    for name, a in ACCOUNTS.items():
        if a["token"] == tok:
            return name
    return None

@app.get("/")
def index():
    return jsonify(app="Race-Bank-API",
                   hint="X-Auth-Token: tok-alice ; GET /balance ; POST /withdraw {amount} ; POST /redeem {code}",
                   seed="alice balance=100, coupon FREE50 (value 50, once)")

@app.get("/balance")
def balance():
    u = who()
    if not u:
        return jsonify(error="bad token"), 401
    return jsonify(user=u, balance=ACCOUNTS[u]["balance"])

@app.post("/withdraw")
def withdraw():
    u = who()
    if not u:
        return jsonify(error="bad token"), 401
    amount = int((request.get_json(force=True, silent=True) or {}).get("amount", 0))
    acct = ACCOUNTS[u]
    # --- TOCTOU: check ... (window) ... then write, no lock ---
    if acct["balance"] >= amount:
        time.sleep(0.15)                 # widen the race window (simulated I/O)
        acct["balance"] -= amount        # parallel requests all passed the check
        resp = {"ok": True, "withdrew": amount, "balance": acct["balance"]}
        if acct["balance"] < 0:
            resp["flag"] = FLAG          # overdrawn -> you beat the guard
        return jsonify(resp)
    return jsonify(ok=False, error="insufficient funds",
                   balance=acct["balance"]), 400

@app.post("/redeem")
def redeem():
    u = who()
    if not u:
        return jsonify(error="bad token"), 401
    code = (request.get_json(force=True, silent=True) or {}).get("code", "")
    c = COUPONS.get(code)
    if not c:
        return jsonify(error="no such coupon"), 404
    # --- TOCTOU: same non-atomic check-then-mark on the coupon ---
    if not c["redeemed"]:
        time.sleep(0.15)
        ACCOUNTS[u]["balance"] += c["value"]
        c["redeemed"] = True
        return jsonify(ok=True, credited=c["value"],
                       balance=ACCOUNTS[u]["balance"])
    return jsonify(ok=False, error="coupon already redeemed"), 400

if __name__ == "__main__":
    print(" * Race-Bank-API on http://0.0.0.0:9012   (threaded; fire parallel requests)")
    app.run(host="0.0.0.0", port=9012, threaded=True)
