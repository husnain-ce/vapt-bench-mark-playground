from utils import render_template, get_time, sanitize_xml
from flask import Flask, request

app = Flask(__name__)

@app.route("/convert", methods=["GET", "POST"])
def convert():
    zone = get_time(
        request.form.get("from_zone", "Europe/Paris"),
        request.form.get("to_zone", "Europe/Paris"),
        request.form.get("time", "12:30")
    )

    if "error" in zone:
        return render_template("error", { **zone }), 500
    else:
        return render_template("convert", { **zone })

if __name__ == "__main__":
    app.run("127.0.0.1", 5000)
