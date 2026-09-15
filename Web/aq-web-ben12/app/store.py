import re

from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flaHIGHNOTE_API_KEY_PLACEHOLDER import current_user, login_required
from markupsafe import escape

from . import db
from .bot import review_bot
from .models import Game, User, user_games

store_bp = Blueprint("store", __name__)

MARKET_ITEMS = [
    {"name": "Vanta Bloom", "finish": "Reactive", "price": "$4.99"},
    {"name": "Jetstream Lattice", "finish": "Animated", "price": "$7.49"},
    {"name": "Sugarcore Drift", "finish": "Iridescent", "price": "$2.19"},
    {"name": "Mono Reactor", "finish": "Carbon", "price": "$5.10"},
    {"name": "Dustline Tape", "finish": "Retro", "price": "$1.89"},
    {"name": "Chrome Daybreak", "finish": "Prismatic", "price": "$6.60"},
]

ACCENTS = {
    "cyan": "#7ef9ff",
    "mint": "#7dffb2",
    "rose": "#ff73d3",
    "gold": "#ffc857",
}


def escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def owns_game(user, game):
    return any(entry.id == game.id for entry in user.library)


def can_view_game(game):
    if game.released:
        return True
    if not current_user.is_authenticated:
        return False
    return current_user.role == "press" or owns_game(current_user, game)


def money(price_cents):
    return f"${price_cents / 100:.2f}"


def capsule_svg(game):
    title = escape(game.title)
    studio = escape(game.studio)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="820" height="460" viewBox="0 0 820 460">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1b2838" />
      <stop offset="100%" stop-color="#101822" />
    </linearGradient>
    <linearGradient id="beam" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{game.accent_a}" stop-opacity="0.85" />
      <stop offset="100%" stop-color="{game.accent_b}" stop-opacity="0.55" />
    </linearGradient>
  </defs>
  <rect width="820" height="460" rx="20" fill="url(#bg)" />
  <rect x="0" y="0" width="820" height="460" fill="#0f1923" opacity="0.25" />
  <path d="M530 0 L820 0 L820 460 L410 460 Z" fill="url(#beam)" opacity="0.76" />
  <circle cx="625" cy="142" r="150" fill="{game.accent_a}" opacity="0.12" />
  <circle cx="690" cy="332" r="176" fill="{game.accent_b}" opacity="0.16" />
  <rect x="38" y="38" width="744" height="384" rx="8" fill="#0c141d" opacity="0.56" />
  <text x="66" y="108" fill="#66c0f4" font-size="20" font-family="Arial, sans-serif" font-weight="700" letter-spacing="5">{studio}</text>
  <text x="66" y="200" fill="#f2f8fd" font-size="58" font-family="Arial, sans-serif" font-weight="700">{title}</text>
  <text x="66" y="252" fill="#c7d5e0" font-size="24" font-family="Arial, sans-serif">{escape(game.tagline)}</text>
  <rect x="66" y="320" width="222" height="50" rx="4" fill="#8bc53f" />
  <text x="112" y="353" fill="#132012" font-size="24" font-family="Arial, sans-serif" font-weight="700">STORE CAPSULE</text>
</svg>"""


@store_bp.app_template_filter("money")
def money_filter(value):
    return money(value)


@store_bp.get("/")
def index():
    q = request.args.get("q", "").strip()
    games_query = Game.query.filter(Game.released.is_(True))
    if q:
        games_query = games_query.filter(Game.title.ilike(f"%{escape_like(q)}%", escape="\\"))
    games = games_query.order_by(Game.featured.desc(), Game.title.asc()).all()
    spotlight_depth = review_bot.depth()
    return render_template(
        "index.html",
        games=games,
        query=q,
        spotlight_depth=spotlight_depth,
        market_items=MARKET_ITEMS[:3],
    )


@store_bp.get("/game/<slug>")
def game(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not can_view_game(game):
        abort(404)
    return render_template("game.html", game=game)


@store_bp.post("/library/add")
@login_required
def add_to_library():
    slug = request.form.get("slug", "").strip()
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not game.released:
        flash("That build is not in the public catalog.")
        return redirect(url_for("store.index"))
    if owns_game(current_user, game):
        flash("Already parked in your library.")
        return redirect(url_for("store.game", slug=slug))
    current_user.library.append(game)
    db.session.commit()
    flash("Added to your library.")
    return redirect(url_for("store.library"))


@store_bp.get("/library")
@login_required
def library():
    q = request.args.get("q", "").strip()
    query = (
        Game.query.join(user_games, user_games.c.game_id == Game.id)
        .filter(user_games.c.user_id == current_user.id)
        .order_by(Game.featured.desc(), Game.title.asc())
    )
    if q:
        query = query.filter(Game.title.ilike(f"%{escape_like(q)}%", escape="\\"))
    games = query.all()
    if current_user.role != "press":
        games = [game for game in games if game.released]
    return render_template("library.html", games=games, query=q)


@store_bp.post("/spotlight/request")
@login_required
def spotlight_request():
    listing = request.form.get("listing", "").strip()
    if not listing:
        abort(400)
    target = current_app.config["SITE_ORIGIN"] + listing
    if review_bot.submit(target):
        flash("A staff capsule check was queued.")
    else:
        flash("The spotlight queue is packed right now.")
    return redirect(request.referrer or url_for("store.index"))


@store_bp.get("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username.lower()).first_or_404()
    games = [game for game in user.library if game.released]
    return render_template("profile.html", profile=user, games=games)


@store_bp.get("/market")
def market():
    q = request.args.get("q", "").strip().lower()
    items = [item for item in MARKET_ITEMS if not q or q in item["name"].lower() or q in item["finish"].lower()]
    return render_template("market.html", items=items, query=q)


@store_bp.get("/support")
def support():
    return render_template("support.html")


@store_bp.post("/support/preview")
def support_preview():
    subject = request.form.get("subject", "").strip()[:80]
    body = request.form.get("body", "").strip()[:800]
    return render_template("partials/support_preview.html", subject=subject, body=body)


@store_bp.post("/community/card/preview")
def community_preview():
    name = request.form.get("name", "").strip()[:24] or "ArcadeGuest"
    status = request.form.get("status", "").strip()[:80] or "Syncing screenshots."
    accent = ACCENTS.get(request.form.get("accent", "cyan"), "#7ef9ff")
    return render_template(
        "partials/community_preview.html",
        name=name,
        status=status,
        accent=accent,
    )


@store_bp.post("/reviews/preview")
def review_preview():
    headline = request.form.get("headline", "").strip()[:48] or "Would queue again."
    body = request.form.get("body", "").strip()[:240] or "The neon was loud. The netcode survived. Five stars."
    return render_template("partials/review_preview.html", headline=headline, body=body)


@store_bp.post("/gift/check")
def gift_check():
    code = request.form.get("code", "").strip().upper()[:32]
    if re.fullmatch(r"[A-Z0-9]{4}(?:-[A-Z0-9]{4}){2,3}", code):
        verdict = "Format looks clean, but this key is not registered."
    else:
        verdict = "Nightbyte keys use grouped uppercase codes."
    return render_template("partials/gift_preview.html", code=code, verdict=verdict)


@store_bp.get("/media/capsule/<slug>.svg")
def capsule(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not can_view_game(game):
        abort(404)
    return Response(capsule_svg(game), mimetype="image/svg+xml")


@store_bp.get("/media/live/<slug>")
def live_capsule(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not can_view_game(game):
        abort(404)
    return render_template("live_capsule.html", game=game)
