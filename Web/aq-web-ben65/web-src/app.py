import os
from flask import Flask, request, render_template_string, make_response

app = Flask(__name__, subdomain_matching=True)
app.config['SERVER_NAME'] = os.getenv("WEB_ORIGIN", 'web.localhost')
SANDBOX_ORIGIN = os.getenv("SANDBOX_ORIGIN", "sandbox.localhost") 


# TO-DO
# Split to different domains 
@app.route('/', subdomain="<sub>")
def subdomain(sub):
    to_sandbox = request.args.get("sandbox", "<h1>Hello Player</h1>")
    url_sandbox = "http://" + SANDBOX_ORIGIN + "/?code=" + to_sandbox
    html = render_template_string("""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Welcome to W4Schools</h1>
            <p>Secret message: {{subdomain}}</p>
            <p>Lesson:</p>
            <iframe sandbox="allow-forms allow-same-origin" src="{{sandbox}}"></iframe>
        </body>
        </html>
        """, subdomain=sub, sandbox=url_sandbox)
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    resp.headers["Content-Security-Policy"] = "script-src 'none'; style-src 'none';"
    return resp


if __name__ == "__main__":
    port = int(os.getenv('FLASK_RUN_PORT', 80))
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
