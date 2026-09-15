from flask import Flask, render_template, request, jsonify, session
from utils import TIMEZONES, SESSIONS, getSession
from datetime import datetime, timedelta
from flaHIGHNOTE_API_KEY_PLACEHOLDER import Session
from lxml import etree
from uuid import uuid4
from re import findall
import random
import pytz
import json

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "./flaHIGHNOTE_API_KEY_PLACEHOLDER"
app.config["SECRET_KEY"] = uuid4()
Session(app)

fields_validators = json.loads(open("validators.json","r").read())

@app.before_request
def initialize_session():
    if not "session_id" in session:
        app.permanent_session_lifetime = timedelta(seconds=int(request.args.get("timeout", 30*60)))
        session["session_id"] = uuid4()

    session["request"] = getSession(session["session_id"])

@app.route("/")
def index():
    timezone_times = {}
    for timezone in random.sample(TIMEZONES, 9):
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz).strftime("%H:%M:%S")
        timezone_times[timezone] = current_time

    return render_template("index.html", timezone_times=timezone_times, all_timezones=TIMEZONES)

@app.route("/api/convert", methods=["POST"])
def convert():
    from_zone = request.form.get("from_zone", "Europe/Paris")
    to_zone = request.form.get("to_zone", "Europe/Paris")
    time = request.form.get("time", "12:30")

    r = session["request"].post("http://backend/convert",
        headers={ "Content-Type": "application/x-www-form-urlencoded" },
        data=f"from_zone={from_zone}&to_zone={to_zone}&time={time}"
    )

    if not r.status_code == 200:
        return { "status_code": r.status_code, "error": r.text }, 500
    
    result = {}
    try:
        parsed_xml = {
            child.tag: child.text
            for child in etree.fromstring(r.text)
        }
        for field_validator in fields_validators:
            field = field_validator["field"]
            if field not in parsed_xml:
                continue

            if field_validator["validator"]["regex"]:
                res = findall(field_validator["validator"]["check"], parsed_xml[field])
                if len(res) > 0:
                    result[field] = res[0]
            else:
                if parsed_xml[field] in TIMEZONES:
                    result[field] = parsed_xml[field]
        return result
    except Exception as e:
        return {"status_code": 500, "error": str(e)}, 500

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
