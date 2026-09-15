# Created with an LLM
import secrets
import uuid
import urllib.parse
import html
import hmac
from pathlib import Path
from typing import Optional, Dict, List
from ipaddress import ip_address

import os
import json
import redis

from fastapi import FastAPI, Request, Response, Form, Query
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
    FileResponse,
    PlainTextResponse,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

SESSION_SECRET = os.getenv("SESSION_SECRET", "@satoki00")

app = FastAPI()

USERS: Dict[str, Dict] = {}
ICON_PATH = Path(__file__).with_name("icon.png")

ADMIN_COOKIE_NAME = "isAdmin"


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def _user_key(u: str) -> str:
    return f"user:{u}"


def get_user_record(u: str):
    data = r.get(_user_key(u))
    if not data:
        return None
    try:
        rec = json.loads(data)
        return rec if isinstance(rec, dict) else None
    except Exception:
        return None


def save_user_record(u: str, data: dict) -> None:
    r.set(_user_key(u), json.dumps(data))


def user_exists(u: str) -> bool:
    return r.exists(_user_key(u)) == 1


def get_notes_for(u: str):
    rec = get_user_record(u)
    return rec.get("notes", []) if rec else []


def set_notes_for(u: str, notes: list):
    rec = get_user_record(u) or {}
    rec["notes"] = notes
    save_user_record(u, rec)


def get_profile_text_for(u: str) -> str:
    rec = get_user_record(u) or {}
    return rec.get("profile_text", "")


def set_profile_text_for(u: str, text: str) -> None:
    rec = get_user_record(u) or {}
    rec["profile_text"] = text
    save_user_record(u, rec)


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        if not request.url.path.startswith("/profile"):
            resp.headers["Content-Security-Policy"] = (
                "default-src'self'; "
                "script-src 'none'; "
                "script-src-elem 'none'; "
                "script-src-attr 'none'; "
                "style-src 'none'; "
                "style-src-elem https://cdnjs.cloudflare.com; "
                "style-src-attr 'none'; "
                "font-src 'none'; "
                "connect-src 'none'; "
                "media-src 'none'; "
                "object-src 'none'; "
                "manifest-src 'none'; "
                "worker-src 'none'; "
                "frame-src 'none'; "
                "child-src 'none'; "
                "prefetch-src 'none'; "
                "base-uri 'none'; "
                "form-action 'self'; "
                "frame-ancestors 'none'; "
                "navigate-to 'self'"
            )
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Permissions-Policy"] = "geolocation=()"
        return resp


class PathGuardMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_path_len: int = 1024):
        super().__init__(app)
        self.max_path_len = max_path_len

    async def dispatch(self, request: Request, call_next):
        if len(request.url.path) > self.max_path_len:
            return PlainTextResponse("Request-URI Too Long", status_code=414)
        return await call_next(request)


app.add_middleware(CSPMiddleware)
app.add_middleware(PathGuardMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
)


def current_user(request: Request) -> Optional[dict]:
    u = request.session.get("user")
    if not u or not isinstance(u, str) or len(u) > 128:
        return None
    rec = get_user_record(u)
    if not rec or "uuid" not in rec:
        request.session.pop("user", None)
        return None
    return {"username": u, **rec}


def e(s: str) -> str:
    return html.escape(s, quote=True)


def csrf_token(request: Request) -> str:
    tok = request.session.get("csrf_token")
    if not tok:
        tok = secrets.token_urlsafe(32)
        request.session["csrf_token"] = tok
    return tok


def verify_csrf(request: Request, token: str) -> bool:
    sess = request.session.get("csrf_token", "")
    return bool(token) and hmac.compare_digest(token, sess)


def valid_password(p: str) -> bool:
    return len(p) >= 8


def _set_admin_cookie(resp: Response, value: str) -> None:
    resp.headers.append(
        "Set-Cookie",
        f"{ADMIN_COOKIE_NAME}={value}; Path=/; HttpOnly; SameSite=Lax; Secure; Partitioned",
    )
    resp.headers.append(
        "Set-Cookie", f"{ADMIN_COOKIE_NAME}={value}; Path=/; HttpOnly; SameSite=Lax"
    )


def _clear_admin_cookie(resp: Response) -> None:
    resp.headers.append(
        "Set-Cookie",
        f"{ADMIN_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Secure; Partitioned; Max-Age=0",
    )
    resp.headers.append(
        "Set-Cookie", f"{ADMIN_COOKIE_NAME}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0"
    )


def _admin_cookie_true(request: Request) -> bool:
    return request.cookies.get(ADMIN_COOKIE_NAME) == "true"


def _has_proxy_like_headers(request: Request) -> bool:
    for k in request.headers.keys():
        lk = k.lower()
        if lk in ("forwarded", "x-real-ip", "via"):
            return True
        if lk.startswith("x-forwarded-"):
            return True
    return False


def _peer_ip(request: Request) -> str:
    c = request.scope.get("client")
    return c[0] if c and isinstance(c, (list, tuple)) and len(c) >= 1 else ""


def _is_loopback_only(host: str) -> bool:
    try:
        ip = ip_address(host)
        return ip.is_loopback
    except Exception:
        return False


def _strict_local_request(request: Request) -> bool:
    if _has_proxy_like_headers(request):
        return False
    return _is_loopback_only(_peer_ip(request))


def _can_render_admin_only(request: Request) -> bool:
    return _strict_local_request(request) and _admin_cookie_true(request)


def header_nav_html(
    request: Request, user: Optional[dict], order_class: str = ""
) -> str:
    token = csrf_token(request)
    if user:
        return f"""
<header class="w-full border-b bg-white {order_class}">
  <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
    <a href="/" class="text-xl font-bold">Note Atelier</a>
    <nav class="flex items-center gap-4">
      <a href="/notes" class="inline-flex items-center h-8 text-sm underline align-middle">Notes</a>
      <a href="/profile/{user['uuid']}" class="inline-flex items-center gap-2 h-8 align-middle">
        <img src="/images/{user['uuid']}.png" alt="avatar" width="28" height="28" class="rounded-full">
        <span class="text-sm">Profile</span>
      </a>
      <form method="POST" action="/logout" class="inline">
        <input type="hidden" name="csrf_token" value="{token}">
        <button type="submit" class="inline-flex items-center h-8 text-sm underline align-middle">Logout</button>
      </form>
    </nav>
  </div>
</header>
"""
    return f"""
<header class="w-full border-b bg-white {order_class}">
  <div class="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
    <a href="/" class="text-xl font-bold">Note Atelier</a>
    <nav class="flex items-center gap-4">
      <a href="/login" class="inline-flex items-center h-8 text-sm underline align-middle">Login</a>
      <a href="/register" class="inline-flex items-center h-8 text-sm underline align-middle">Register</a>
    </nav>
  </div>
</header>
"""


def render_page(title: str, body_inner: str) -> str:
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} - Note Atelier</title>
  <meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'none';
    script-src-elem 'none';
    script-src-attr 'none';
    style-src 'none';
    style-src-elem https://cdnjs.cloudflare.com;
    style-src-attr 'none';
    font-src 'none';
    connect-src 'none';
    media-src 'none';
    object-src 'none';
    manifest-src 'none';
    worker-src 'none';
    frame-src 'none';
    child-src 'none';
    prefetch-src 'none';
    base-uri 'none';
    form-action 'self';
    frame-ancestors 'none';
    navigate-to 'self'
  ">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css">
</head>
<body class="min-h-screen bg-gray-50">
  {body_inner}
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def top(request: Request, name: str = Query("", max_length=256)):
    user = current_user(request)
    if not name and user:
        name = user["username"]
    if "cloudflare" in name.lower():
        name = "Hacker"
    greet = (
        """
<h1 class="text-3xl font-semibold max-w-5xl mx-auto px-6 py-6">Hello, Guest!</h1>
"""
        if not user
        else f"""
<h1 class="text-3xl font-semibold max-w-5xl mx-auto px-6 py-6">Welcome {name}</h1>
"""
    )
    body = f"""
<div class="flex flex-col">
  <div class="order-last">
    {greet}
  </div>
  {header_nav_html(request, user, order_class="order-first")}
</div>
"""
    return HTMLResponse(render_page(f"Welcome {name}", body))


@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    user = current_user(request)
    token = csrf_token(request)
    body = f"""
{header_nav_html(request, user)}
<main class="max-w-5xl mx-auto px-6 py-10">
  <section class="max-w-md mx-auto bg-white p-6 rounded-xl shadow">
    <h2 class="text-2xl font-semibold mb-4">Login</h2>
    <form method="POST" action="/login" class="space-y-4">
      <input type="hidden" name="csrf_token" value="{token}">
      <div>
        <label for="u" class="block text-sm font-medium mb-1">Username</label>
        <input id="u" name="u" type="text" required class="w-full border rounded-md px-3 py-2" autocomplete="username">
      </div>
      <div>
        <label for="p" class="block text-sm font-medium mb-1">Password</label>
        <input id="p" name="p" type="password" required class="w-full border rounded-md px-3 py-2" autocomplete="current-password">
      </div>
      <div class="pt-2">
        <button type="submit" class="w-full rounded-md px-4 py-2 border">Sign in</button>
      </div>
    </form>
  </section>
</main>
"""
    return HTMLResponse(render_page("Login", body))


@app.post("/login")
async def login_post(
    request: Request, u: str = Form(...), p: str = Form(...), csrf_token: str = Form("")
):
    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Login Failed",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )
    rec = get_user_record(u)
    if not rec or rec["password"] != p:
        return HTMLResponse(
            render_page(
                "Login Failed",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>Invalid credentials.</p></main>",
            )
        )
    request.session["user"] = u
    resp = RedirectResponse(f"/?name={urllib.parse.quote_plus(u)}", status_code=303)
    _set_admin_cookie(resp, "false")
    return resp


@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    user = current_user(request)
    token = csrf_token(request)
    body = f"""
{header_nav_html(request, user)}
<main class="max-w-5xl mx-auto px-6 py-10">
  <section class="max-w-md mx-auto bg-white p-6 rounded-xl shadow">
    <h2 class="text-2xl font-semibold mb-4">Register</h2>
    <form method="POST" action="/register" class="space-y-4">
      <input type="hidden" name="csrf_token" value="{token}">
      <div>
        <label for="u" class="block text-sm font-medium mb-1">Username</label>
        <input id="u" name="u" type="text" required class="w-full border rounded-md px-3 py-2" autocomplete="username">
      </div>
      <div>
        <label for="p" class="block text-sm font-medium mb-1">Password (8+ chars)</label>
        <input id="p" name="p" type="password" required class="w-full border rounded-md px-3 py-2" autocomplete="new-password" minlength="8">
      </div>
      <div class="pt-2">
        <button type="submit" class="w-full rounded-md px-4 py-2 border">Create account</button>
      </div>
    </form>
  </section>
</main>
"""
    return HTMLResponse(render_page("Register", body))


@app.post("/register")
async def register_post(
    request: Request, u: str = Form(...), p: str = Form(...), csrf_token: str = Form("")
):
    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Register",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )
    if user_exists(u):
        return HTMLResponse(
            render_page(
                "Register",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>Username already taken.</p></main>",
            )
        )
    if not valid_password(p):
        return HTMLResponse(
            render_page(
                "Register",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm text-red-600'>Password must be at least 8 characters.</p></main>",
            ),
            status_code=400,
        )
    uid = uuid.uuid4().hex
    save_user_record(u, {"password": p, "uuid": uid, "notes": [], "profile_text": ""})
    request.session["user"] = u
    resp = RedirectResponse(f"/?name={urllib.parse.quote_plus(u)}", status_code=303)
    _set_admin_cookie(resp, "false")
    return resp


@app.post("/logout")
async def logout(request: Request, csrf_token: str = Form("")):
    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Logout",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )
    request.session.clear()
    resp = RedirectResponse("/", status_code=303)
    _clear_admin_cookie(resp)
    return resp


@app.get("/notes", response_class=HTMLResponse)
async def notes_index(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    token = csrf_token(request)
    notes = get_notes_for(user["username"])
    items = []
    for n in notes:
        badge = (
            '<span class="ml-2 text-xs px-2 py-0.5 border rounded">AdminOnly</span>'
            if n.get("admin_only")
            else ""
        )
        items.append(
            f"""
<li class="py-2 flex items-center justify-between">
  <a class="underline" href="/notes/{n['id']}">{e(n['title'])}</a>{badge}
  <form method="POST" action="/notes/{n['id']}/delete">
    <input type="hidden" name="csrf_token" value="{token}">
    <button type="submit" class="text-sm underline">Delete</button>
  </form>
</li>
""".strip()
        )
    items_html = (
        "\n".join(items)
        if items
        else "<li class='py-2 text-gray-500'>No notes yet</li>"
    )
    body = f"""
{header_nav_html(request, user)}
<main class="max-w-5xl mx-auto px-6 py-10">
  <section class="grid md:grid-cols-2 gap-6">
    <div class="bg-white p-6 rounded-xl shadow">
      <h2 class="text-xl font-semibold mb-4">Create a Note</h2>
      <form method="POST" action="/notes" class="space-y-4">
        <input type="hidden" name="csrf_token" value="{token}">
        <div>
          <label for="title" class="block text-sm font-medium mb-1">Title</label>
          <input id="title" name="title" type="text" required class="w-full border rounded-md px-3 py-2">
        </div>
        <div>
          <label for="content" class="block text-sm font-medium mb-1">Content</label>
          <textarea id="content" name="content" rows="6" required class="w-full border rounded-md px-3 py-2"></textarea>
        </div>
        <div class="flex items-center gap-2">
          <input id="admin_only" name="admin_only" type="checkbox" value="1" class="h-4 w-4">
          <label for="admin_only" class="text-sm">AdminOnly</label>
        </div>
        <div class="pt-2">
          <button type="submit" class="w-full rounded-md px-4 py-2 border">Save</button>
        </div>
      </form>
    </div>
    <div class="bg-white p-6 rounded-xl shadow">
      <h2 class="text-xl font-semibold mb-4">Your Notes</h2>
      <ul class="list-disc list-inside">
        {items_html}
      </ul>
    </div>
  </section>
</main>
"""
    return HTMLResponse(render_page("Notes", body))


@app.post("/notes")
async def notes_create(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    admin_only: Optional[str] = Form(None),
    csrf_token: str = Form(""),
):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Notes",
                header_nav_html(request, user)
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )
    note_id = uuid.uuid4().hex[:12]
    notes = get_notes_for(user["username"])
    notes.append(
        {
            "id": note_id,
            "title": title,
            "content": content,
            "admin_only": bool(admin_only),
        }
    )
    set_notes_for(user["username"], notes)
    return RedirectResponse("/notes", status_code=303)


@app.get("/notes/{note_id}", response_class=HTMLResponse)
async def notes_show(request: Request, note_id: str):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    notes = get_notes_for(user["username"])
    note = next((n for n in notes if n["id"] == note_id), None)
    if not note:
        return RedirectResponse("/notes", status_code=303)
    token = csrf_token(request)
    if note.get("admin_only") and not _can_render_admin_only(request):
        content_html = "<div class='text-sm text-gray-500 italic'>AdminOnly: rendering suppressed (loopback admin only).</div>"
    else:
        content_html = (
            f"<pre class='whitespace-pre-wrap text-sm'>{e(note['content'])}</pre>"
        )
    badge = (
        '<span class="ml-2 text-xs px-2 py-0.5 border rounded">AdminOnly</span>'
        if note.get("admin_only")
        else ""
    )
    body = f"""
{header_nav_html(request, user)}
<main class="max-w-5xl mx-auto px-6 py-10">
  <section class="max-w-2xl mx-auto bg-white p-6 rounded-xl shadow space-y-4">
    <h2 class="text-2xl font-semibold">{e(note['title'])}{badge}</h2>
    {content_html}
    <div class="pt-2 flex gap-4">
      <a href="/notes" class="underline">Back</a>
      <form method="POST" action="/notes/{note_id}/delete">
        <input type="hidden" name="csrf_token" value="{token}">
        <button type="submit" class="text-sm underline">Delete</button>
      </form>
    </div>
  </section>
</main>
"""
    return HTMLResponse(render_page("Note", body))


@app.post("/notes/{note_id}/delete")
async def notes_delete(request: Request, note_id: str, csrf_token: str = Form("")):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Notes",
                header_nav_html(request, user)
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )
    notes: List[Dict] = get_notes_for(user["username"])
    notes = [n for n in notes if n["id"] != note_id]
    set_notes_for(user["username"], notes)
    return RedirectResponse("/notes", status_code=303)


@app.get("/profile/{user_uuid}", response_class=HTMLResponse)
async def profile_get(
    request: Request,
    user_uuid: str,
    name: str = Query("", max_length=256),
):
    user = current_user(request)
    if not name and user:
        name = user["username"]
    if "cloudflare" in name.lower():
        name = "Hacker"
    if not user or user_uuid != user["uuid"]:
        return RedirectResponse("/", status_code=303)
    pt = get_profile_text_for(user["username"])
    profile_text = pt or "<em class='text-gray-500'>No profile yet</em>"
    token = csrf_token(request)
    body = f"""
{header_nav_html(request, user)}
<main class="max-w-5xl mx-auto px-6 py-10">
  <section class="max-w-xl mx-auto bg-white p-6 rounded-xl shadow space-y-6">
    <div class="flex items-center gap-4">
      <img src="/images/{user['uuid']}.png" alt="avatar" width="64" height="64" class="rounded-full border">
      <div>
        <h2 class="text-2xl font-semibold">{name}</h2>
        <p class="text-sm font-mono">{user['uuid']}</p>
      </div>
    </div>
    <div class="p-4 border rounded bg-gray-50">
      {profile_text}
    </div>
    <div>
      <h3 class="text-lg font-semibold mb-2">Edit Profile</h3>
      <form method="POST" action="/profile/{user['uuid']}" class="space-y-4">
        <input type="hidden" name="csrf_token" value="{token}">  <!-- ★ 追加 -->
        <div>
          <label for="profile_text" class="block text-sm font-medium mb-1">Profile HTML</label>
          <textarea id="profile_text" name="profile_text" rows="6" class="w-full border rounded-md px-3 py-2">{get_profile_text_for(user['username'])}</textarea>
        </div>
        <div>
          <button type="submit" class="rounded-md px-4 py-2 border">Save</button>
        </div>
      </form>
    </div>
  </section>
</main>
"""
    return HTMLResponse(render_page(f"{name} Profile", body))


@app.post("/profile/{user_uuid}")
async def profile_post(
    request: Request,
    user_uuid: str,
    profile_text: str = Form(""),
    csrf_token: str = Form(""),
):
    user = current_user(request)
    if not user or user_uuid != user["uuid"]:
        return RedirectResponse("/", status_code=303)

    if not verify_csrf(request, csrf_token):
        return HTMLResponse(
            render_page(
                "Profile",
                header_nav_html(request, current_user(request))
                + "<main class='max-w-5xl mx-auto px-6 py-10'><p class='text-sm'>CSRF verification failed.</p></main>",
            ),
            status_code=403,
        )

    set_profile_text_for(user["username"], profile_text)
    return RedirectResponse(f"/profile/{user['uuid']}", status_code=303)


@app.get("/images/{user_uuid}.png")
async def avatar_png(user_uuid: str):
    if not ICON_PATH.exists():
        return Response(status_code=404)
    return FileResponse(ICON_PATH, media_type="image/png")
