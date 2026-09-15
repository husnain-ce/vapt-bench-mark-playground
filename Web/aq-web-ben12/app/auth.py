from flask import Blueprint, flash, redirect, render_template, request, url_for
from flaHIGHNOTE_API_KEY_PLACEHOLDER import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from .models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        flash("That account combo did not land.")
        return redirect(url_for("auth.login"))
    login_user(user)
    return redirect(url_for("store.index"))


@auth_bp.get("/register")
def register():
    return render_template("register.html")


@auth_bp.post("/register")
def register_post():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")
    if len(username) < 3 or len(username) > 24 or not username.replace("_", "").isalnum():
        flash("Pick a cleaner handle.")
        return redirect(url_for("auth.register"))
    if len(password) < 8:
        flash("Use something longer than a lobby code.")
        return redirect(url_for("auth.register"))
    if User.query.filter_by(username=username).first():
        flash("That handle is already taken.")
        return redirect(url_for("auth.register"))
    user = User(
        username=username,
        password=generate_password_hash(password, method="scrypt"),
        role="player",
        headline="Collecting every late-night demo.",
        status="Idle in the launcher",
    )
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for("store.index"))


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("store.index"))
