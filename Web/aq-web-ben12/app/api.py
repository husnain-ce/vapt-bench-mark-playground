import hashlib

from flask import Blueprint, jsonify, request
from flaHIGHNOTE_API_KEY_PLACEHOLDER import current_user, login_required

from .models import Game

api_bp = Blueprint("api", __name__)


def escape_like(value):
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@api_bp.get("/api/search")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    escaped = escape_like(q)
    games = (
        Game.query.filter(Game.released.is_(True), Game.title.ilike(f"%{escaped}%", escape="\\"))
        .order_by(Game.featured.desc(), Game.title.asc())
        .limit(6)
        .all()
    )
    return jsonify(
        [{"slug": game.slug, "title": game.title, "studio": game.studio} for game in games]
    )


@api_bp.post("/api/quote")
def quote():
    payload = request.get_json(silent=True) or {}
    slugs = payload.get("items", [])
    coupon = str(payload.get("coupon", "")).strip().upper()
    games = Game.query.filter(Game.released.is_(True), Game.slug.in_(slugs)).all()
    subtotal = sum(game.price_cents for game in games)
    if coupon == "AFTERGLOW":
        subtotal = max(subtotal - 499, 0)
    stamp = hashlib.sha1(f"{slugs}:{coupon}:{subtotal}".encode()).hexdigest()[:12]
    return jsonify(
        {
            "items": len(games),
            "subtotal": subtotal,
            "currency": "USD",
            "stamp": stamp,
        }
    )


@api_bp.get("/api/build/<slug>")
def build(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    if not game.released:
        return jsonify({"status": "archived", "channel": "internal"})
    return jsonify(
        {
            "slug": game.slug,
            "channel": "stable",
            "featured": game.featured,
            "genre": game.genre,
        }
    )


@api_bp.get("/api/me")
@login_required
def me():
    return jsonify(
        {
            "username": current_user.username,
            "headline": current_user.headline,
            "library_count": len(current_user.library),
        }
    )
