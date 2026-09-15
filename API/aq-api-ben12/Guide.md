Target 2. VAmPI — REST  ✅ (verified working via Docker on this box)

1: deployment Command: docker run -d --name vampi -p 5000:5000 erev0s/vampi:latest
Open in brower:  http://localhost:5000/ui   |   seed data: curl http://localhost:5000/createdb
# Quick win: curl http://localhost:5000/users/v1/_debug   (leaks plaintext passwords)
2: Stop:  docker rm -f vampi
```
No-Docker fallback (Python venv, Py 3.13/3.14):

1: Clone it: git clone https://github.com/erev0s/VAmPI && cd VAmPI
2: python Envirment: python3 -m venv .venv && . .venv/bin/activate
3: Requirments: pip install -r requirements.txt && pip install -U "sqlalchemy>=2.0.36"   # fix for Py 3.13+
vulnerable=1 python app.py
```
Requirments: Docker , Requirments.txt

List of Vulnerabilities

    SQLi Injection
    Unauthorized Password Change
    Broken Object Level Authorization
    Mass Assignment
    Excessive Data Exposure through debug endpoint
    User and Password Enumeration
    RegexDOS (Denial of Service)
    Lack of Resources & Rate Limiting
    JWT authentication bypass via weak signing key

