Target 3. vAPI — REST (OWASP API Top 10)  ✅ (verified working via Docker on this box)

1: Go to the repo: git clone https://github.com/roottusk/vapi && cd vapi)
2: Deploy Command:  docker compose up -d --build
Open in browser:  http://localhost:8000/vapi/     <-- documentation + challenge index (NOT bare http://localhost)
                  http://localhost:8001/          <-- phpMyAdmin (root / vapi123456)
Import into Postman:  ./vapi/postman/vAPI.postman_collection.json  +  vAPI_ENV.postman_environment.json
   (or use the public workspace: https://www.postman.com/roottusk/workspace/vapi/)
# Quick win: curl http://localhost:8000/vapi/api3/comment    (Excessive Data Exposure — leaks deviceid = flag{api3_...})
3: Stop:  docker compose down          (add -v to also wipe the MySQL volume "persistent")

WHY BARE http://localhost DID NOT WORK (the bug in the old readme):
   compose maps host 8000 -> container 80, and `artisan serve` listens on container port 80 (SERVER_PORT=80).
   So the app is on port 8000, and all content lives under /vapi/. Use http://localhost:8000/vapi/ .
   The API base URL for every challenge below is:  http://localhost:8000/vapi/
```
No-Docker fallback (manual install — needs PHP 7.4/8.0 + Composer + a running MySQL):

1: Clone it:      git clone https://github.com/roottusk/vapi && cd vapi/vapi
2: Dependencies:  composer install
3: Database:      create DB `vapi`, then import ../database/vapi.sql   (mysql -uroot -p vapi < ../database/vapi.sql)
4: Config:        cp .env.example .env  &&  edit .env  (set DB_HOST=127.0.0.1, DB_DATABASE=vapi, DB_USERNAME/DB_PASSWORD),
                  then:  php artisan key:generate  &&  php artisan config:cache
5: Serve:         php artisan serve            # http://localhost:8000/vapi/
```
Requirements:
    Docker + docker compose          (easy path — all you need)
    PHP 7.4/8.0, Composer, MySQL     (manual path only)
    Postman                          (drive the challenge collection)
    MITM proxy (Burp / mitmproxy)    (intercept & tamper requests)

List of Vulnerabilities (OWASP API Security Top 10 — 2019):

    API1  Broken Object Level Authorization (BOLA/IDOR)   -> GET  api1/user/{id}    (swap the id, needs auth header)
    API2  Broken User Authentication                      -> POST api2/user/login   (weak/guessable creds + token reuse)
    API3  Excessive Data Exposure                         -> GET  api3/comment      (leaks deviceid/lat/long — quick win)
    API4  Lack of Resources & Rate Limiting               -> POST api4/otp/verify   (brute-force the OTP, no throttling)
    API5  Broken Function Level Authorization (BFLA)       -> GET  api5/users        (user reaches an admin-only listing)
    API6  Mass Assignment                                 -> POST api6/user         (inject the `credit` field on register)
    API7  Security Misconfiguration                       -> GET  api7/user/key,login (verbose errors / exposed key)
    API8  Injection (SQLi)                                -> POST api8/user/login   (SQLi to reach api8/user/secret)
    API9  Improper Assets Management                      -> POST api9/v1 vs v2/user/login (old v1 lacks the v2 rate limit)
    API10 Insufficient Logging & Monitoring              -> GET  api10/user/flag
    Bonus  JustWeakToken (JWT)                            -> POST/GET jwt/user      (forge a weakly-signed JWT)
    Bonus  ServerSurfer (SSRF)                            -> GET  serversurfer?url= (reach internal /flag.txt -> flag{ssrf_...})

Submit flags at:  http://localhost:8000/vapi/  (Flag Submit Dashboard)  |  API: GET /vapi/dashboard/flag
