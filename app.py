from flask import Flask
from flask import redirect, render_template, request
import sqlite3

app = Flask(__name__)


@app.route("/")
def index():
    db = sqlite3.connect("database.db")
    posts = db.execute("SELECT content FROM posts").fetchall()
    db.close()
    count = len(posts)
    return render_template("index.html", count=count, posts=posts)


@app.route("/new")
def new():
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    content = request.form["content"]
    db = sqlite3.connect("database.db")
    db.execute("INSERT INTO posts (content) VALUES (?)", [content])
    db.commit()
    db.close()
    return redirect("/")


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/result", methods=["POST"])
def result():
    message = request.form["message"]
    return render_template("result.html", message=message)


@app.route("/page1")
def page1():
    return "Tämä on sivu 1"


@app.route("/page2")
def page2():
    return "Tämä on sivu 2"
