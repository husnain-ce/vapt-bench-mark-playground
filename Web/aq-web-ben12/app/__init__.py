import os
import secrets

from flask import Flask
from flaHIGHNOTE_API_KEY_PLACEHOLDER import LoginManager
from flaHIGHNOTE_API_KEY_PLACEHOLDER import SQLAlchemy
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy(session_options={"expire_on_commit": False})
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(24))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.environ.get('DB_PATH', '/data/nightbyte.db')}"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {"check_same_thread": False},
        "pool_pre_ping": True,
    }
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SITE_ORIGIN"] = os.environ.get("SITE_ORIGIN", "https://localhost:5000")
    app.config["PRESS_USER"] = os.environ.get("PRESS_USER", "pressdesk")
    app.config["PRESS_PASS"] = os.environ.get("PRESS_PASS", "neonvault")

    db.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .auth import auth_bp
    from .store import store_bp
    from .api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.session.execute(text("PRAGMA journal_mode=WAL"))
        db.session.execute(text("PRAGMA synchronous=NORMAL"))
        db.session.commit()

    if os.environ.get("DISABLE_BOT") != "1":
        from .bot import review_bot

        review_bot.configure(
            site_origin=app.config["SITE_ORIGIN"],
            username=app.config["PRESS_USER"],
            password=app.config["PRESS_PASS"],
        )
        review_bot.start()

    return app
