import os
import re
import html
import urllib.parse as urlparse
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import secrets

APP_BASE = os.getenv("APP_BASE", "http://127.0.0.1:8000").rstrip("/")
FLAG_CONTENT = os.getenv("FLAG", "flag{dummy_flag}")
VISIT_TIMEOUT_MS = int(os.getenv("VISIT_TIMEOUT_MS", "3000"))
app = FastAPI(title="Non-Admin Bot")


def page_shell(title: str, body: str) -> HTMLResponse:
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(title)}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50">
  <header class="w-full border-b bg-red-600 text-white">
    <div class="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
      <h1 class="text-xl font-bold tracking-tight">Non-Admin Bot</h1>
    </div>
  </header>
  <main class="max-w-3xl mx-auto px-6 py-8">
    {body}
  </main>
</body>
</html>"""
    return HTMLResponse(html_doc)


def _normalize_target(target: str) -> str:
    t = (target or "").strip()
    if not t:
        raise ValueError("URL is empty")
    parsed = urlparse.urlparse(t)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return t
    raise ValueError(
        "Only absolute http(s) URLs are allowed. Relative paths are rejected."
    )


async def _register(page, username: str, password: str) -> None:
    await page.goto(f"{APP_BASE}/register", wait_until="domcontentloaded")
    await page.fill("#u", username)
    await page.fill("#p", password)
    await page.click('button[type="submit"]')
    await page.wait_for_url(re.compile(r".*[?&]name="))


async def _create_adminonly_note_on_notes(page, title: str, content: str) -> None:
    await page.goto(f"{APP_BASE}/notes", wait_until="domcontentloaded")
    note_form = (
        page.locator("form")
        .filter(has=page.locator("#title"))
        .filter(has=page.locator("#content"))
    )
    await page.fill("#title", title)
    await page.fill("#content", content)
    if await page.locator("#admin_only").count() > 0:
        await page.check("#admin_only")
    submit = note_form.locator('button[type="submit"], input[type="submit"]')
    if await submit.count() == 0:
        submit = page.locator(
            'button[type="submit"]:not(:has-text("Logout")),'
            'input[type="submit"]:not([value="Logout"])'
        )
    async with page.expect_response(
        lambda r: r.request.method in ["POST"] and "/notes" in r.url
    ):
        await submit.first.click()
    await page.wait_for_load_state("networkidle")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    form = """
    <section class="bg-white p-6 rounded-2xl shadow">
      <form method="POST" action="/visit" class="space-y-4">
        <div>
          <label for="url" class="block text-sm font-medium mb-1">URL</label>
          <input id="url" name="url" type="url" required placeholder="https://example.com/" class="w-full border rounded-md px-3 py-2">
          <p class="text-xs text-slate-500 mt-1">Only absolute http(s) URLs. Relative paths are rejected.</p>
        </div>
        <div class="pt-2">
          <button type="submit" class="w-full rounded-md px-4 py-2 border border-red-600 text-red-700 hover:bg-red-600 hover:text-white transition">Submit</button>
        </div>
      </form>
    </section>
    """
    return page_shell("Non-Admin Bot", form)


@app.post("/visit", response_class=HTMLResponse)
async def visit_form(url: str = Form(...)):
    try:
        target = _normalize_target(url)
    except ValueError as e:
        return page_shell(
            "Non-Admin Bot - Error",
            f"<section class='bg-white p-6 rounded-2xl shadow'><p class='text-red-600 text-sm'>{html.escape(str(e))}</p><p class='pt-3'><a class='underline text-red-700 hover:text-red-800' href='/'>Back</a></p></section>",
        )

    admin_user = f"satoki_{secrets.token_hex(16)}"  # Non-Admin
    admin_pass = secrets.token_urlsafe(24)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, args=["--no-sandbox", "--js-flags=--noexpose_wasm,--jitless"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        await _register(page, admin_user, admin_pass)
        await _create_adminonly_note_on_notes(page, title="flag", content=FLAG_CONTENT)

        try:
            await page.goto(target, wait_until="load", timeout=VISIT_TIMEOUT_MS)
        except Exception:
            pass
        await page.wait_for_timeout(3000)
        landing = page.url

        await context.close()
        await browser.close()

    body = f"""
    <section class="bg-white p-6 rounded-2xl shadow space-y-3">
      <h2 class="text-lg font-semibold">Done</h2>
      <p class="text-sm">A non-admin accessed your site!</p>
      <div class="pt-2">
        <a href="/" class="underline text-red-700 hover:text-red-800">Back</a>
      </div>
    </section>
    """
    return page_shell("Non-Admin Bot - Result", body)
