Target 5. Pixi — REST (OWASP DevSlop Pixi, MEAN-stack API)  ⏳ NOT run here (re-confirmed 2026-09-01) — needs node:8 + the seeded deadrobots/pixi:datastore image; both stall mid-layer on this host's throttled Docker Hub blob CDN (retried today, never finalize), and native is blocked (transitive 'fibers' native dep will not compile on this box's Node 24). Runs normally via `docker compose up -d` on a working Docker Hub.

Pixi is a deliberately vulnerable MongoDB/Express/Angular/Node ("MEAN") photo-sharing app built by OWASP DevSlop to teach API security. A front-end talks to a JSON API you attack directly.

1: Get the repo:   unzip Pixi.zip && cd Pixi        # (fresh box: git clone https://github.com/DevSlop/Pixi && cd Pixi)
2: Deploy Command: docker compose up -d             # builds the app image, pulls the seeded Mongo datastore
Open in browser:   http://localhost:8000/           <-- Pixi web app
                   http://localhost:8090/            <-- REST API base (attack surface)
                   Mongo: 27017  |  Mongo HTTP: 28017
# Quick win: Mass Assignment — register and smuggle privileged fields (is_admin / balance) in the JSON body to /api/register; the API trusts them
3: Stop:  docker compose down          (add -v to wipe the Mongo volume)

Requirements:
    Docker + docker compose          (app + seeded MongoDB datastore)
    Postman / Burp / curl            (drive and tamper the JSON API)

List of Vulnerabilities:

    Mass Assignment (register/update with is_admin / balance fields)
    NoSQL Injection (MongoDB query operators in login/search)
    Broken Object Level Authorization (IDOR on user / picture objects)
    Excessive Data Exposure (user PII, card token, admin balance in API responses)
    Broken Authentication / weak & guessable JWT
    Plaintext / weakly-stored credentials
    Reflected & Stored XSS
    Unrestricted file upload
    No rate limiting on auth endpoints
