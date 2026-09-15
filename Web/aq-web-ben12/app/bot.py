import queue
import threading
import os

from playwright.sync_api import sync_playwright


class ReviewBot:
    def __init__(self):
        self._queue = queue.Queue(maxsize=256)
        self._threads = []
        self._lock = threading.Lock()
        self._site_origin = None
        self._username = None
        self._password = None
        self._workers = max(int(os.environ.get("BOT_WORKERS", "4")), 1)
        self._visit_ms = max(int(os.environ.get("BOT_VISIT_MS", "15000")), 1000)

    def configure(self, site_origin, username, password):
        self._site_origin = site_origin.rstrip("/")
        self._username = username
        self._password = password

    def start(self):
        with self._lock:
            if self._threads:
                return
            for _ in range(self._workers):
                thread = threading.Thread(target=self._loop, daemon=True)
                thread.start()
                self._threads.append(thread)

    def submit(self, target):
        try:
            self._queue.put_nowait(target)
            return True
        except queue.Full:
            return False

    def depth(self):
        return self._queue.qsize()

    def _refresh_storage(self, browser):
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.goto(f"{self._site_origin}/login", wait_until="networkidle", timeout=20000)
        page.fill('input[name="username"]', self._username)
        page.fill('input[name="password"]', self._password)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{self._site_origin}/", timeout=20000)
        storage_state = context.storage_state()
        context.close()
        return storage_state

    def _visit(self, browser, storage_state, target):
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1440, "height": 900},
            storage_state=storage_state,
        )
        page = context.new_page()
        page.goto(target, wait_until="load", timeout=20000)
        page.wait_for_timeout(self._visit_ms)
        context.close()

    def _loop(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-infobars",
                    "--disable-extensions",
                ],
            )
            storage_state = None
            while True:
                target = self._queue.get()
                try:
                    if storage_state is None:
                        storage_state = self._refresh_storage(browser)
                    self._visit(browser, storage_state, target)
                except Exception:
                    storage_state = None
                finally:
                    self._queue.taHIGHNOTE_API_KEY_PLACEHOLDER()


review_bot = ReviewBot()
