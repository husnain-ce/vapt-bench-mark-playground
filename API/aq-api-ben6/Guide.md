Target 1. crAPI — REST + GraphQL (OWASP flagship "Completely Ridiculous API")  ✅ (verified working via Docker on this box — every crapi/* image + postgres:14/mongo:4.4/chromadb/mailhog is already cached locally, so the full stack comes up healthy; skip the `pull` step, the blob CDN is throttled here but the images are present)

OWASP's flagship API-security learning platform: a car-dealership app (identity, community/forum, workshop, chatbot, web UI + an API gateway) deliberately seeded with the OWASP API Security Top 10. Multi-service Docker stack — 5 crapi services + Postgres + Mongo + ChromaDB + MailHog (catches signup/OTP emails). Heavier than every other lab in this set; there is no single-file source, so the "repo" is the compose file that pulls the images.

1: Get the repo:   unzip OWASP_FlagShip.zip && cd OWASP_FlagShip     (contains docker-compose.yml)
2: Deploy Command:  docker compose -f docker-compose.yml -p crapi up -d      # images already cached here; the `pull` step is throttled on this host so skip it
Open in browser:   http://localhost:8888            <-- crAPI web UI (register a user first)
                   http://localhost:8025            <-- MailHog (read the signup/OTP/password-reset emails)
# Quick win (Excessive Data Exposure): the community forum API leaks other users' email + vehicle id:
#   curl -s http://localhost:8888/community/api/v2/community/posts/recent   ->  author email/nickname/vehicleid of OTHER users
# Then swap a leaked vehicleid into the vehicle-location endpoint (BOLA, Challenge 1).
3: Stop:  docker compose -p crapi down          (add -v to also wipe the postgres/mongo/chroma volumes)

Seed:  no fixed creds — self-register at http://localhost:8888, then confirm via the OTP email shown in MailHog (http://localhost:8025). A second account is needed for the cross-user (BOLA/BFLA) challenges.

Requirements:
    Docker + docker compose          (only supported path — pulls crapi/*, postgres:14, mongo:4.4, chromadb, mailhog)
    Working Docker Hub access        (the images are NOT bundled — this host's pull is blocked)
    MailHog @ :8025                  (built into the stack — read OTP / reset emails here)
    Postman + MITM proxy (Burp)      (drive the API and intercept/tamper requests)

Challenges (map to the vuln list below):
    C1  BOLA — read another user's vehicle details/location (find + swap the vehicle GUID)
    C2  BOLA — read another user's "contact mechanic" report (increment the report id)
    C3  Broken Auth — reset a DIFFERENT user's password (predictable reset endpoint / brute OTP)
    C4  Excessive Data Exposure — endpoint leaking other users' sensitive info  (quick win)
    C5  Excessive Data Exposure — internal property of a video resource
    C6  Rate Limiting — layer-7 DoS via the "contact mechanic" feature
    C7  BFLA — delete another user's video via a predictable admin endpoint
    C8  Mass Assignment — get an item for free (edit order properties on a shadow endpoint)
    C9  Mass Assignment — refund yourself $1,000+ (chain from C8)
    C10 Mass Assignment — write an internal video property (chain from C5)
    C11 SSRF — make crAPI fetch www.google.com and return the response
    C12 NoSQL Injection — obtain free coupons without knowing the code
    +2  two undisclosed "secret" challenges

List of Vulnerabilities (OWASP API Security Top 10):

    API1  Broken Object Level Authorization (BOLA/IDOR)  -> vehicle details (C1), mechanic reports (C2)
    API2  Broken User Authentication                     -> password reset of another user (C3)
    API3  Excessive Data Exposure                        -> user PII (C4) + internal video property (C5)
    API4  Lack of Resources & Rate Limiting              -> L7 DoS via contact-mechanic (C6)
    API5  Broken Function Level Authorization (BFLA)      -> delete another user's video (C7)
    API6  Mass Assignment                                -> free item (C8), balance +$1000 (C9), video prop (C10)
    API7  SSRF                                           -> force crAPI to call www.google.com (C11)
    API8  Injection (NoSQL)                              -> free coupons without the code (C12)
    Bonus GraphQL surface + 2 secret challenges
