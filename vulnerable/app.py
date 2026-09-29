import hashlib
import sqlite3
import subprocess

from flask import Flask, request, render_template_string, session

app = Flask(__name__)
app.secret_key = "super-secret-key-123"  # VULN: secret en dur (Information disclosure)

DB = "shop.db"


def get_db():
    return sqlite3.connect(DB)


def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, password TEXT, role TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY, owner INTEGER, body TEXT)")
    if not db.execute("SELECT 1 FROM users").fetchone():
        md5 = lambda p: hashlib.md5(p.encode()).hexdigest()
        db.execute("INSERT INTO users(name,password,role) VALUES('admin',?, 'admin')", (md5("admin123"),))
        db.execute("INSERT INTO users(name,password,role) VALUES('alice',?, 'user')", (md5("alice"),))
        db.execute("INSERT INTO notes(owner,body) VALUES(1,'Note confidentielle admin')")
        db.execute("INSERT INTO notes(owner,body) VALUES(2,'Note de alice')")
    db.commit()


@app.route("/")
def index():
    return "<h1>Vulnerable Notes App</h1><a href='/login'>login</a>"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        pwd = hashlib.md5(request.form["password"].encode()).hexdigest()  # VULN: MD5 sans sel
        # VULN: injection SQL (Tampering / Elevation of privilege)
        q = "SELECT id, role FROM users WHERE name='%s' AND password='%s'" % (name, pwd)
        row = get_db().execute(q).fetchone()
        if row:
            session["uid"], session["role"] = row
            return "Bienvenue " + name
        return "Identifiants invalides", 401  # pas de limitation de tentatives
    return "<form method=post>name <input name=name> pwd <input name=password type=password><input type=submit></form>"


@app.route("/search")
def search():
    term = request.args.get("q", "")
    # VULN: XSS réfléchi (Tampering / Information disclosure)
    return render_template_string("<h2>Résultats pour " + term + "</h2>")


@app.route("/notes/<int:note_id>")
def note(note_id):
    # VULN: IDOR, aucun contrôle de propriété (Information disclosure)
    row = get_db().execute("SELECT body FROM notes WHERE id=%d" % note_id).fetchone()
    return row[0] if row else ("Introuvable", 404)


@app.route("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # VULN: injection de commande (Elevation of privilege)
    return subprocess.check_output("ping -c 1 " + host, shell=True)


@app.route("/admin")
def admin():
    # VULN: contrôle d'accès basé sur un paramètre client (Spoofing / EoP)
    if request.args.get("admin") == "1":
        return "Panneau admin"
    return "Interdit", 403


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)  # VULN: debug=True
