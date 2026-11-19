import os
import secrets
import sqlite3
from datetime import date
from functools import wraps
from pathlib import Path

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

MAX_POST_LENGTH = 1000
# Compared against unknown emails so login takes the same time either way.
DUMMY_HASH = generate_password_hash(secrets.token_hex(16), method="pbkdf2:sha256:600000")

app = Flask(__name__)
app.config.update(
    DATABASE=Path(__file__).with_name("social.db"),
    # ponytail: random key logs everyone out on restart, set FLASK_SECRET_KEY when deployed.
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_SAMESITE="Lax",
)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.before_request
def load_user():
    user_id = session.get("userID")
    g.user = (
        get_db().execute("SELECT userID, username FROM Users WHERE userID = ?", (user_id,)).fetchone()
        if user_id
        else None
    )


def login_required(view):
    @wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped


def get_own_post(post_id):
    """Return the post, or stop with 404 if missing and 403 if someone else's."""
    post = get_db().execute("SELECT * FROM Posts WHERE postID = ?", (post_id,)).fetchone()
    if post is None:
        abort(404)
    if post["userID"] != g.user["userID"]:
        abort(403)
    return post


def submitted_content():
    """Return the trimmed form content, or None after flashing what is wrong."""
    content = request.form.get("content", "").strip()
    if not content:
        flash("Post cannot be empty.", "error")
        return None
    if len(content) > MAX_POST_LENGTH:
        flash(f"Post must be {MAX_POST_LENGTH} characters or fewer.", "error")
        return None
    return content


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = (
            get_db()
            .execute(
                "SELECT userID, password FROM Users WHERE email = ?",
                (request.form.get("email", "").strip().lower(),),
            )
            .fetchone()
        )
        stored_hash = user["password"] if user else DUMMY_HASH
        if check_password_hash(stored_hash, request.form.get("password", "")) and user:
            session.clear()
            session["userID"] = user["userID"]
            return redirect(url_for("feed"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def feed():
    """Your posts plus posts from accepted friends, newest first."""
    posts = (
        get_db()
        .execute(
            """
            SELECT p.postID, p.userID, p.content, p.postDate, u.username
            FROM Posts p
            JOIN Users u ON u.userID = p.userID
            WHERE p.userID = :me
               OR p.userID IN (
                    SELECT userID2 FROM Friendships WHERE userID1 = :me AND status = 1
                    UNION
                    SELECT userID1 FROM Friendships WHERE userID2 = :me AND status = 1
               )
            ORDER BY p.postDate DESC, p.postID DESC
            """,
            {"me": g.user["userID"]},
        )
        .fetchall()
    )
    return render_template("posts.html", title="Your feed", posts=posts, show_form=True,
                           max_length=MAX_POST_LENGTH)


@app.get("/users/<int:user_id>/posts")
@login_required
def user_posts(user_id):
    author = get_db().execute("SELECT username FROM Users WHERE userID = ?", (user_id,)).fetchone()
    if author is None:
        abort(404)
    posts = (
        get_db()
        .execute(
            """
            SELECT p.postID, p.userID, p.content, p.postDate, u.username
            FROM Posts p
            JOIN Users u ON u.userID = p.userID
            WHERE p.userID = ?
            ORDER BY p.postDate DESC, p.postID DESC
            """,
            (user_id,),
        )
        .fetchall()
    )
    return render_template("posts.html", title=f"Posts by {author['username']}", posts=posts,
                           show_form=False, max_length=MAX_POST_LENGTH)


@app.post("/posts")
@login_required
def create_post():
    content = submitted_content()
    if content:
        db = get_db()
        with db:
            db.execute(
                "INSERT INTO Posts (userID, content, postDate) VALUES (?, ?, ?)",
                (g.user["userID"], content, date.today().isoformat()),
            )
        flash("Post shared.", "success")
    return redirect(url_for("feed"))


@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = get_own_post(post_id)
    if request.method == "POST":
        content = submitted_content()
        if content:
            db = get_db()
            with db:
                db.execute("UPDATE Posts SET content = ? WHERE postID = ?", (content, post_id))
            flash("Post updated.", "success")
            return redirect(url_for("feed"))
    return render_template("edit_post.html", post=post,
                           content=request.form.get("content", post["content"]),
                           max_length=MAX_POST_LENGTH)


@app.post("/posts/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    get_own_post(post_id)
    db = get_db()
    with db:  # The schema has no ON DELETE CASCADE, so remove child rows first.
        db.execute("DELETE FROM Comments WHERE postID = ?", (post_id,))
        db.execute("DELETE FROM Likes WHERE postID = ?", (post_id,))
        db.execute("DELETE FROM Posts WHERE postID = ?", (post_id,))
    flash("Post deleted.", "success")
    return redirect(url_for("feed"))
