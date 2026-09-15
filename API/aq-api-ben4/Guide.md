Target 9. Generic-University — REST (InsiderPhD's Laravel API practice app)  ⏳ NOT run here (re-confirmed 2026-09-01) — Laravel 7 requires PHP <= 8.0 (this box has PHP 8.4) so native is blocked, and its Docker image (busk3r/genericuniversity) stalls mid-layer on this host's throttled Docker Hub (retried today). Runs normally on PHP 7.x/8.0 + MySQL or via its Docker image on a working Docker Hub.

Generic University is a deliberately vulnerable Laravel web app + REST API (students, professors, courses, grades) used throughout InsiderPhD's "API Hacking" course to practise finding authorization and data-exposure bugs with Postman/Burp.

1: Get the repo:   unzip Generic-University.zip && cd Generic-University   # (fresh box: git clone https://github.com/InsiderPhD/Generic-University)
2: Deploy Command: docker run -d --name genuni -p 8888:80 busk3r/genericuniversity        # (or native — see fallback below)
Open in browser:   http://localhost:8888/            <-- web app; REST API under /api/
# Quick win: Excessive Data Exposure / IDOR — the /api/ endpoints return more fields (and other users records) than the web UI shows; walk /api/users and /api/users/{id}
3: Stop:  docker rm -f genuni
```
No-Docker fallback (native Laravel, uses the bundled composer.phar):

1: php composer.phar install
2: cp .env.example .env  &&  php artisan key:generate
3: configure DB in .env (MySQL), then:  php artisan migrate --seed
4: php artisan serve            # http://localhost:8000  (API under /api/)
```
Requirements:
    Docker  OR  PHP 8.x + Composer + MySQL
    Postman / Burp / curl            (walk the /api/ endpoints)

List of Vulnerabilities:

    Broken Object Level Authorization (IDOR on student / grade / user objects)
    Broken Function Level Authorization (reach admin-only actions)
    Excessive Data Exposure (API returns more fields than the UI shows)
    Mass Assignment (set privileged fields on create/update)
    Improper Assets Management (old / undocumented API versions)
    Broken Authentication (weak token / password reset)
    SQL Injection
