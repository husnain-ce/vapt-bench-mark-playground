from flaHIGHNOTE_API_KEY_PLACEHOLDER import UserMixin

from . import db

user_games = db.Table(
    "user_games",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("game_id", db.Integer, db.ForeignKey("game.id"), primary_key=True),
    db.Index("ix_user_games_user_id", "user_id"),
    db.Index("ix_user_games_game_id", "game_id"),
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="player", index=True)
    headline = db.Column(db.String(80), nullable=False, default="Queueing another patch.")
    status = db.Column(db.String(120), nullable=False, default="Online")
    accent = db.Column(db.String(7), nullable=False, default="#7ef9ff")
    library = db.relationship("Game", secondary=user_games, lazy="selectin", order_by="Game.title")


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    studio = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    price_cents = db.Column(db.Integer, nullable=False, default=0)
    released = db.Column(db.Boolean, nullable=False, default=True, index=True)
    featured = db.Column(db.Boolean, nullable=False, default=False, index=True)
    accent_a = db.Column(db.String(7), nullable=False, default="#7ef9ff")
    accent_b = db.Column(db.String(7), nullable=False, default="#ff4ecd")
    blurb = db.Column(db.Text, nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
