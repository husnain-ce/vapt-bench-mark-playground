Target 11. JWT-Forge-API — REST (Python / Flask, hand-rolled JWT)  ✅ (verified working via native run on this box)

A tiny, deliberately vulnerable JWT authentication service. Unlike the other labs (which only ship a *weak signing secret*), here the **verifier itself is broken**: it trusts attacker-controlled header fields (`alg`, `kid`, `jwk`). Log in as an ordinary user, then forge a `role:admin` token three different ways to reach `/admin` and grab the flag. No external JWT library — the signing/verifying is hand-rolled so every flaw is real and self-contained.

1: Get the repo:   unzip JWT-Forge-API.zip && cd JWT-Forge-API
2: Deploy (native — verified here):  ./run.sh        # (or: python3 app.py)  needs Flask (pip install flask)
Open in browser:   http://localhost:9011/           <-- {"app":"JWT-Forge-API",...}
# Quick win: forge an alg:none admin token (no signature, no secret needed):
#   T=$(python3 -c "import base64,json;b=lambda x:base64.urlsafe_b64encode(json.dumps(x,separators=(',',':')).encode()).rstrip(b'=').decode();print(b({'alg':'none','typ':'JWT'})+'.'+b({'sub':'alice','role':'admin'})+'.')")
#   curl -s localhost:9011/admin -H "Authorization: Bearer $T"   ->  {"flag":"flag{jwt_alg0_c0nfusi0n_pwned}",...}
3: Stop:  Ctrl-C  (or: kill the app.py process)

Seed users:  alice/alice123 , bob/bob123   (both role=user — /admin needs role=admin, which you FORGE)
Real (but weak) HMAC secret: secret123   (brute-forceable — the intended fallback path)

Requirements:
    Python 3 + Flask                (native run — no Docker, no DB)
    Postman / Burp / curl           (craft & tamper JWTs)

Endpoints:
    POST /login   {username,password}  -> returns an HS256 token (role=user)
    GET  /me                           -> echoes your verified claims
    GET  /admin                        -> role=admin only -> returns the flag

List of Vulnerabilities (all verified on this box):

    JWT alg:none accepted — signature stripped, token trusted as-is
    JWT kid path traversal — the `kid` header is used as a key *filename*; point it at a
        missing/attacker-chosen file (e.g. kid="../../../../nonexistent") -> empty key -> forgeable
    JWT jwk header injection — the token carries its own key in the `jwk` header; the server
        verifies the signature against the attacker-supplied key
    Weak HMAC secret ("secret123") — the intended fallback signing key is trivially brute-forceable
    Broken Function Level Authorization — /admin trusts the (forgeable) `role` claim
