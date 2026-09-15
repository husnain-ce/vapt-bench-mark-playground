import os
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__)

BOT_ORIGIN = "http://" + os.getenv("BOT_ORIGIN", "bot.localhost")
SANDBOX_ORIGIN = "http://" + os.getenv("SANDBOX_ORIGIN", "sandbox.localhost")


@app.route('/')
def sandbox():
    code = request.args.get("code", "<h1>hello</h1>")
    html = render_template_string("""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Welcome to Sandbox Domain</h1>
            <p> Test whatever you want, you won't be able to escape</p>
            <h3>Report URL to Bot</h3>
            <form action='""" + BOT_ORIGIN + """/report' method="POST">
                <input name="code" placeholder="{{ code | urlencode}}" required>
                <button type="submit">Report to Bot</button>
            </form>
            <p>{{ code|safe }}</p>
        </body>
        </html>
        """, code=code, SANDBOX_ORIGIN=SANDBOX_ORIGIN)
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers["Content-Security-Policy"] = "script-src 'none'; style-src 'none';"
    return resp


if __name__ == "__main__":
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
