import ipaddress
import logging
import os
import sqlite3
import subprocess
from functools import wraps

from flask import Flask, abort, request, session
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]  # FIX: secret hors du code
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
logging.basicConfig(level=logging.INFO)  # FIX: journalisation (Repudiation)

DB = "shop.db"
failed = {}  # FIX: limitation basique des tentatives (Flask-Limiter en prod)


def get_db():
    return sqlite3.connect(DB)


def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, password TEXT, role TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, owner INTEGER, body TEXT)")
    if not db.execute("SELECT 1 FROM users").fetchone():
        db.execute("INSERT INTO users(name,password,role) VALUES('admin',?, 'admin')", (generate_password_hash("admin123"),))
        db.execute("INSERT INTO users(name,password,role) VALUES('alice',?, 'user')", (generate_password_hash("alice"),))
        db.execute("INSERT INTO notes(owner,body) VALUES(1,'Note confidentielle admin')")
        db.execute("INSERT INTO notes(owner,body) VALUES(2,'Note de alice')")
    db.commit()


def login_required(role=None):
    def deco(f):
        @wraps(f)
        def wrapper(*a, **kw):
            if "uid" not in session:
                abort(401)
            if role and session.get("role") != role:
                abort(403)
            return f(*a, **kw)
        return wrapper
    return deco


@app.after_request
def headers(resp):  # FIX: en-têtes de sécurité (signalés par ZAP)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    return resp


@app.route("/")
def index():
    return "<h1>Notes App (fixed)</h1><a href='/login'>login</a>"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        if failed.get(name, 0) >= 5:
            abort(429)
        row = get_db().execute("SELECT id, role, password FROM users WHERE name=?", (name,)).fetchone()  # FIX: paramétrée
        if row and check_password_hash(row[2], request.form["password"]):
            session["uid"], session["role"] = row[0], row[1]
            app.logger.info("login ok user=%s", name)
            return "Bienvenue " + str(escape(name))
        failed[name] = failed.get(name, 0) + 1
        app.logger.warning("login failed user=%s", name)
        return "Identifiants invalides", 401
    return "<form method=post>name <input name=name> pwd <input name=password type=password><input type=submit></form>"


@app.route("/search")
def search():
    return "<h2>Résultats pour " + str(escape(request.args.get("q", ""))) + "</h2>"  # FIX: échappement


@app.route("/notes/<int:note_id>")
@login_required()
def note(note_id):
    row = get_db().execute("SELECT body FROM notes WHERE id=? AND owner=?", (note_id, session["uid"])).fetchone()  # FIX: IDOR
    return row[0] if row else abort(404)


@app.route("/ping")
@login_required("admin")
def ping():
    try:
        host = str(ipaddress.ip_address(request.args.get("host", "127.0.0.1")))  # FIX: validation stricte
    except ValueError:
        abort(400)
    return subprocess.check_output(["ping", "-c", "1", host])  # FIX: pas de shell


@app.route("/admin")
@login_required("admin")  # FIX: rôle vérifié côté serveur
def admin():
    return "Panneau admin"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
