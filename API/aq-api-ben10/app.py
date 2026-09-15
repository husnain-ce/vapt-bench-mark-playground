#!/usr/bin/env python3
"""
Target 13. Template-Forge-API  -- deliberately vulnerable to SERVER-SIDE TEMPLATE
INJECTION (SSTI). Focus: Jinja2 SSTI -> RCE, a class NONE of the other 10 cover.
User input is concatenated into a template string and rendered server-side, so
{{ ... }} expressions execute in the Jinja sandbox-free context -> full RCE.

Run:  python3 app.py      (needs Flask;  pip install flask  if missing)
"""
import os
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
PROFILES = {}                     # username -> bio (for the stored-SSTI path)
FLAG = "flag{sst1_jinja2_rce}"

@app.get("/")
def index():
    return jsonify(app="Template-Forge-API",
                   hint="GET /greeting?name=  |  POST /render {template}  |  POST /profile {user,bio} + GET /card/<user>",
                   quick_win="GET /greeting?name={{7*7}}  -> renders 49",
                   flag_file="/flag.txt is on disk; read it via SSTI RCE")

# VULN A: reflected SSTI -- user input spliced straight into the template
@app.get("/greeting")
def greeting():
    name = request.args.get("name", "guest")
    return render_template_string("<h1>Hello " + name + "!</h1>")

# VULN B: direct template evaluation -- render whatever the user sends
@app.post("/render")
def render():
    tpl = (request.get_json(force=True, silent=True) or {}).get("template", "")
    try:
        return jsonify(result=render_template_string(tpl))
    except Exception as e:
        return jsonify(error=str(e)), 400

# VULN C: stored SSTI -- bio saved now, rendered later on the profile card
@app.post("/profile")
def set_profile():
    d = request.get_json(force=True, silent=True) or {}
    PROFILES[d.get("user", "anon")] = d.get("bio", "")
    return jsonify(ok=True, user=d.get("user", "anon"))

@app.get("/card/<user>")
def card(user):
    bio = PROFILES.get(user, "no bio yet")
    return render_template_string(
        "<div class=card><b>" + user + "</b><p>" + bio + "</p></div>")

def _plant_flag():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "flag.txt")
    open(path, "w").write(FLAG + "\n")
    return path

if __name__ == "__main__":
    print(" * flag planted at:", _plant_flag())
    print(" * Template-Forge-API on http://0.0.0.0:9013")
    app.run(host="0.0.0.0", port=9013)
