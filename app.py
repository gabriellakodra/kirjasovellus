from flask import Flask
from flask import redirect, render_template, request
import sqlite3
from werkzeug.security import generate_password_hash
import db


app = Flask(__name__)


@app.route("/")
def index():
    posts = db.query("SELECT content FROM posts")
    count = len(posts)
    return render_template("index.html", count=count, posts=posts)


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"


@app.route("/new")
def new():
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    db.execute("INSERT INTO posts (content) VALUES (?)", [content])
    return redirect("/")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/result", methods=["POST"])
def result():
    message = request.form["message"]
    return render_template("result.html", message=message)
