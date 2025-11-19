# FILE: app/web.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import User, MonitoredURL
from app.auth import verify_password, get_password_hash
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize database on startup
init_db()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()

        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists", "error")
            db.close()
            return redirect(url_for("register"))

        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        session["user_id"] = new_user.id
        session["username"] = new_user.username
        db.close()

        flash("Registration successful!", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.query(User).filter(User.username == username).first()

        if user and verify_password(password, user.password_hash):
            session["user_id"] = user.id
            session["username"] = user.username
            db.close()
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        db.close()
        flash("Invalid username or password", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()
    user = db.query(User).filter(User.id == session["user_id"]).first()
    urls = db.query(MonitoredURL).filter(
        MonitoredURL.user_id == session["user_id"],
        MonitoredURL.is_active == True
    ).all()
    db.close()

    return render_template("dashboard.html", user=user, urls=urls)


@app.route("/add_url", methods=["POST"])
def add_url():
    if "user_id" not in session:
        return redirect(url_for("login"))

    url = request.form.get("url")

    if not url:
        flash("URL is required", "error")
        return redirect(url_for("dashboard"))

    # Basic URL validation
    if not url.startswith(("http://", "https://")):
        flash("URL must start with http:// or https://", "error")
        return redirect(url_for("dashboard"))

    db = get_db()

    # Check if URL already exists for this user
    existing_url = db.query(MonitoredURL).filter(
        MonitoredURL.user_id == session["user_id"],
        MonitoredURL.url == url,
        MonitoredURL.is_active == True
    ).first()

    if existing_url:
        flash("This URL is already being monitored", "error")
        db.close()
        return redirect(url_for("dashboard"))

    # Add new URL
    new_url = MonitoredURL(
        url=url,
        user_id=session["user_id"]
    )
    db.add(new_url)
    db.commit()
    db.close()

    flash(f"Started monitoring {url}", "success")
    return redirect(url_for("dashboard"))


@app.route("/remove_url/<int:url_id>", methods=["POST"])
def remove_url(url_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db()

    # Find the URL and verify it belongs to the current user
    monitored_url = db.query(MonitoredURL).filter(
        MonitoredURL.id == url_id,
        MonitoredURL.user_id == session["user_id"]
    ).first()

    if not monitored_url:
        flash("URL not found", "error")
        db.close()
        return redirect(url_for("dashboard"))

    # Mark as inactive instead of deleting (preserves historical data)
    monitored_url.is_active = False
    db.commit()
    db.close()

    flash(f"Stopped monitoring {monitored_url.url}", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
