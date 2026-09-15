Target 4. DVGA — GraphQL (Damn Vulnerable GraphQL Application)  ✅ (verified working via Docker on this box — the dvga:latest image is already built locally; you MUST pass WEB_HOST=0.0.0.0 or the app binds 127.0.0.1 INSIDE the container and the port map gives connection-refused)

DVGA is a deliberately insecure GraphQL server (Flask + Graphene) for learning and practising GraphQL-specific attacks. Ships in Beginner and Expert difficulty modes (toggle in the web UI).

1: Get the repo:   unzip DVGA.zip && cd DVGA        # (fresh box: git clone https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application && cd Damn-Vulnerable-GraphQL-Application)
2: Deploy Command: docker build -t dvga .   # (image dvga:latest already built here)
   Run:            docker run -d --name dvga -p 5013:5013 -e WEB_HOST=0.0.0.0 -e WEB_PORT=5013 dvga
Open in browser:   http://localhost:5013/          <-- web UI  |  GraphiQL IDE at http://localhost:5013/graphiql
                   GraphQL endpoint (attack surface):  http://localhost:5013/graphql
# Quick win: GraphQL introspection is ON — dump the whole schema:  curl -s http://localhost:5013/graphql -H "Content-Type: application/json" -d "{\"query\":\"{__schema{types{name}}}\"}"
3: Stop:  docker rm -f dvga        (image stays cached; `docker rmi dvga` to remove it too)

Requirements:
    Docker                          (easy path — all you need)
    Python 3.7+ + pip               (no-Docker path: pip install -r requirements.txt && python app.py -> :5013)
    A GraphQL client / Burp / curl  (send raw queries & introspection)

List of Vulnerabilities (GraphQL Security):

    Denial of Service — Batch Query / deeply-nested / alias-based query flooding
    GraphQL Introspection enabled (full schema disclosure)
    GraphQL Field Suggestions (schema leakage even with introspection off)
    Discovering & Fingerprinting the GraphQL engine
    OS Command Injection (x2 — via query and mutation)
    SQL Injection
    Authorization Bypass
    GraphQL JWT Token Forge (weak signing key)
    GraphQL Interface / IDE Protection Bypass
    GraphQL Query Deny List Bypass
    Weak Password protection on a GraphQL mutation
    Arbitrary File Write / Path Traversal
    Log Spoofing / Log Injection
    HTML Injection / Stored XSS
