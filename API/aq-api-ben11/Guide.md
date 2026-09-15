Target 6. Tiredful-API — REST (Django REST Framework)  ⏳ NOT run here (re-confirmed 2026-09-01) — the base alpine:3.6 image IS cached, but the image build's `apk add` fetch against the EOL Alpine v3.6 mirror (dl-cdn) hangs on this host, and the app is Django 1.11 / Python 2 which will not run on this box's Python 3.14. Runs normally in its Docker image / a Python 2 env on a box with reachable Alpine-3.6 repos.

Tiredful API is an intentionally broken REST web service (Django + Django REST Framework) that teaches the common coding mistakes behind API vulnerabilities. Each "resource" is a self-contained exercise.

1: Get the repo:   unzip Tiredful-API.zip && cd Tiredful-API   # (fresh box: git clone https://github.com/payatu/Tiredful-API)
2: Deploy Command: docker build -t tiredful . && docker run -d --name tiredful -p 8000:8000 tiredful
Open in browser:   http://localhost:8000/          <-- documentation + exercises index
# Quick win: IDOR — walk the resource IDs:  curl http://localhost:8000/api/v1/resources/1/  then increment the id to read other users records
3: Stop:  docker rm -f tiredful
```
No-Docker fallback (the container image is old — Alpine 3.6/Python 2; use this if the build fails):

1: python3 -m venv .venv && . .venv/bin/activate
2: pip install -r requirements.txt          # (Django + DRF; pin versions from requirements.txt)
3: cd Tiredful-API && python manage.py migrate
4: python manage.py runserver 0.0.0.0:8000  # add --insecure if static files don't load
```
Requirements:
    Docker                          (easy path)
    Python + pip, SQLite            (no-Docker path)
    Postman / Burp / curl           (send API requests with the bearer token)

List of Vulnerabilities:

    Information Disclosure (verbose errors / debug data)
    Broken Object Level Authorization (IDOR on resource IDs)
    Broken Authentication (predictable / weak bearer & JWT tokens)
    SQL Injection (SQLite backend)
    Cross Origin Resource Sharing (permissive CORS)
    Missing Rate Limiting / Throttling
    Mass Assignment
    Information Exposure through headers
