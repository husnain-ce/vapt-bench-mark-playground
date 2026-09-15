Target 10. vulnerable-api — REST (Python Bottle "vAPI" demo)  ✅ (verified working via native run on this box)

A compact Python (Bottle) API with a users table and a token table, written to illustrate the most common API attacks on a tiny surface — a good warm-up target. NOTE: the published Docker image (mkam/vulnerable-api-demo) uses a Docker manifest *schema 1*, which modern Docker (v25+) has REMOVED — so it will NOT pull. Run it from source instead (below); the source is patched for Python 3.

1: Get the repo:   unzip vulnerable-api.zip && cd vulnerable-api
2: Deploy (native):  ./run-native.sh
   (equivalently:  cd ansible/roles/api/files && python3 -m venv venv && ./venv/bin/pip install bottle lxml && ./venv/bin/python vAPI.py)
Open in browser:   http://localhost:8081/          <-- {"Application":"vulnerable-api","Status":"running"}
# Quick win: get a token, then leak another user's password:
#   TOKEN=$(curl -s -H 'Content-type: application/json' -X POST localhost:8081/tokens -d '{"auth":{"passwordCredentials":{"username":"user1","password":"pass1"}}}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access"]["token"]["id"])')
#   curl -s -H "X-Auth-Token: $TOKEN" localhost:8081/user/1     ->  {"user":{"id":1,"name":"user1","password":"pass1"}}
3: Stop:  Ctrl-C  (or: kill the vAPI.py process)

Requirements:
    Python 3 + pip (bottle, lxml)    (native run — no Docker needed)
    Postman / Burp / curl            (request tokens, then hit protected endpoints)
    Seed users: user1/pass1, user2/pass2, user3/pass3

List of Vulnerabilities (all verified on this box):

    SQL Injection — /tokens auth bypass:  password  "x' OR '1'='1"  returns a valid token without the real password
    SQL Injection — /user/<id>:  0' OR '1'='1  dumps a user record regardless of id
    Excessive Data Exposure — GET /user/{id} returns the cleartext password field
    Broken Authentication — tokens never actually expire (expiry is checked but ignored)
    Broken Object Level Authorization (IDOR) — user ids are sequential and guessable
    XXE / Billion Laughs — POST /tokens with Content-Type: application/xml parses external entities (lxml resolve_entities=True)
    ReDoS — catastrophic regex in POST /user  ("([a-z]+)*[0-9]")
