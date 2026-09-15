import os
import sys
import time
from threading import Thread
from urllib.parse import quote
from flask import Flask, request
from playwright.sync_api import sync_playwright


app = Flask(__name__)

WEB_ORIGIN = os.getenv("WEB_ORIGIN", "web.localhost")
SANDBOX_ORIGIN = os.getenv("SANDBOX_ORIGIN", "sandbox.localhost")
FLAG = os.getenv("FLAG", "ctf{REDACTED}").replace("{", "").replace("}", "")


def visit_web(code):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            for FLAG_CHAR in FLAG:
                visit = f"http://{FLAG_CHAR}.{WEB_ORIGIN}/?sandbox=" + quote(code)
                print(f"[BOT] Visiting {visit}")
                sys.stdout.flush()
                page.goto(visit)
                time.sleep(3)
                print(f"[BOT] Visited {visit}")
                sys.stdout.flush()
        except Exception as e:
            print(f"[BOT] Failed to visit {WEB_ORIGIN}: {e}")
            sys.stdout.flush()


@app.route('/report', methods=['POST'])
def report():
    code = request.form.get('code')
    if not code: 
        return "no url! error!"

    Thread(target=visit_web, args=(code,)).start()
    return "Sent to the bot!"


@app.route("/")
def status():
    return "Bot is running!"


if __name__ == "__main__":
    # Start background thread to visit web continuously
    app.run(host="0.0.0.0", port=1337)
