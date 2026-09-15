from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import send_file
from string import Template
from json import loads
from io import BytesIO
from re import match
import pytz

TIMEZONES = loads(open("timezones.json", "r").read())

def sanitize_xml(xml):
    if not type(xml) == str:
        return xml

    forbidden_chars = ["&","<",">",'"',"%"]
    for forbidden_char in forbidden_chars:
        xml = xml.replace(forbidden_char, "")

    return xml

def calculate_angles(time):
    hour, minute = map(int, time.split(":"))
    hour_angle = (hour % 12) * 30 + (minute / 60) * 30
    minute_angle = (minute / 60) * 360
    return hour_angle, minute_angle

def check_time_format(time):
    pattern = r'^[0-2][0-9]:[0-5][0-9]$'
    if not match(pattern, time):
        raise ValueError(f"time data '{time}' does not match format '%H:%M'") 

def check_zone_value(zone):
    if not zone in TIMEZONES:
        raise ValueError(f"zone data '{zone}' isn't allowed") 

def get_time(from_zone, to_zone, time):
    try:
        check_time_format(time)
        check_zone_value(from_zone)
        check_zone_value(to_zone)

        time = datetime.strptime(time, "%H:%M")
        localized_time = pytz.timezone(from_zone).localize(time)
        converted_time = localized_time.astimezone(pytz.timezone(to_zone)).strftime("%H:%M")

        from_hour_angle, from_minute_angle = calculate_angles(localized_time.strftime("%H:%M"))
        to_hour_angle, to_minute_angle = calculate_angles(converted_time)

        return {
            "converted_time": sanitize_xml(converted_time),
            "from_zone": sanitize_xml(from_zone),
            "to_zone": sanitize_xml(to_zone),
            "from_hour_angle": sanitize_xml(from_hour_angle),
            "from_minute_angle": sanitize_xml(from_minute_angle),
            "to_hour_angle": sanitize_xml(to_hour_angle),
            "to_minute_angle": sanitize_xml(to_minute_angle)
        }
    except Exception as e:
        return {
            "error": sanitize_xml(str(e)),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def render_template(view, variables):
    tmpl = Template(open(f"views/{view}.xml", "r").read())
    res  = tmpl.safe_substitute(variables)
    return send_file(BytesIO(res.encode()), mimetype="text/xml")
