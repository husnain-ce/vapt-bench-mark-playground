from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from requests import session
from json import loads

TIMEZONES = loads(open("timezones.json", "r").read())
SESSIONS  = {}

def getSession(uuid):
    if not uuid in SESSIONS:
        SESSIONS[uuid] = session()
    return SESSIONS[uuid]

# This is not part of the challenge. I just want to make sure the challenge doesn't get DOS :D
def clear_session():
    global SESSIONS
    SESSIONS = {}

scheduler = BackgroundScheduler()
scheduler.add_job(clear_session, "interval", minutes=1)
scheduler.start()
