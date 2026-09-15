import os
import sys
import time
from flask import Flask, request
from threading import Thread
from playwright.sync_api import sync_playwright


app = Flask(__name__)

FLAG = os.getenv("FLAG", "ctf{REDACTED}")
BOT_VISIT = os.getenv('WEB_ORIGIN', 'http://web')


def visit_web(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Visit your URL first, to avoid any attack
            print(f"[BOT] Visiting {url}")
            sys.stdout.flush()
            page.goto(url)
            time.sleep(5)

            # Register and log as admin
            print("[BOT] Login & registering")
            sys.stdout.flush()
            page.goto(BOT_VISIT + '/register')
            page.fill("input[name='username']", FLAG)
            page.fill("input[name='password']", "password")
            page.click("input[type='submit']")
            time.sleep(1)
            page.goto(BOT_VISIT + '/login')
            page.fill("input[name='username']", FLAG)
            page.fill("input[name='password']", "password")
            page.click("input[type='submit']")
            time.sleep(1)

            # Do some admin stuff
            print("[BOT] Admin stuff")
            sys.stdout.flush()
            time.sleep(5)
        except Exception as e:
            print(f"[BOT] Failed to visit {url}: {e}")
            sys.stdout.flush()
        print("[BOT] Finished")
        sys.stdout.flush()
        context.close()
        browser.close()


@app.route("/visit", methods=['POST'])
def visit():
    url = request.form.get('url', None)
    
    if not url:
        return "No url!"

    Thread(target=visit_web, args=(url,)).start()
    return "Bot is running!"


@app.route("/")
def status():
    return "Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337)
