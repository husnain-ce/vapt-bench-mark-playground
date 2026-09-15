Target 12. Race-Bank-API — REST (Python / Flask, threaded)  ✅ (verified working via native run on this box)

A minimal wallet API that is correct for one request at a time but falls apart under concurrency. Every guard is a non-atomic check-then-write with a widened race window, so firing N requests in parallel beats the "once only" logic — classic TOCTOU. This vuln class appears in NONE of the other 10 labs. Served threaded so parallel requests actually overlap.

1: Get the repo:   unzip Race-Bank-API.zip && cd Race-Bank-API
2: Deploy (native — verified here):  ./run.sh        # (or: python3 app.py)  needs Flask
Open in browser:   http://localhost:9012/           <-- {"app":"Race-Bank-API",...}
# Quick win: overdraw a balance of 100 by firing 20 parallel withdrawals of 100:
#   seq 20 | xargs -P20 -I_ curl -s localhost:9012/withdraw -H 'X-Auth-Token: tok-alice' \
#            -H 'Content-Type: application/json' -d '{"amount":100}' >/dev/null
#   curl -s localhost:9012/balance -H 'X-Auth-Token: tok-alice'   ->  {"balance":-1900,...}  (race won)
3: Stop:  Ctrl-C  (or: kill the app.py process)

Seed:  user alice, token = tok-alice, balance = 100 ; coupon FREE50 (value 50, meant to redeem once)

Requirements:
    Python 3 + Flask                (native run — no Docker, no DB)
    curl + xargs / Burp Intruder / Turbo Intruder   (send requests IN PARALLEL — the whole point)

Endpoints:
    GET  /balance                 -> current balance
    POST /withdraw  {amount}      -> check balance>=amount ... (window) ... then deduct   [RACE]
    POST /redeem    {code}        -> check !redeemed ... (window) ... then credit + mark  [RACE]

List of Vulnerabilities (all verified on this box):

    Race Condition / TOCTOU — /withdraw double-spend: parallel requests all pass the balance
        check before any deduct lands -> balance driven negative (overdraw)
    Race Condition / TOCTOU — /redeem coupon multi-redemption: a "once only" coupon credits
        many times when redeemed in parallel
    No locking / non-atomic check-then-write anywhere in the money path
