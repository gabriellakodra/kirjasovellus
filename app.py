from flask import Flask
from flask import redirect, render_template, request, session
import sqlite3, db, config, forum
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    posts = forum.get_posts()
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


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])[0]
    user_id = result[0]
    password_hash = result[1]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")


@app.route("/new")
def new():
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    title = request.form["title"]
    content = request.form["content"]
    user_id = session.get("user_id")

    post_id = forum.add_post(title, content, user_id)
    return redirect("/post/" + str(post_id))


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/result", methods=["POST"])
def result():
    message = request.form["message"]
    return render_template("result.html", message=message)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = forum.get_post(post_id)
    comments = forum.get_comments(post_id)
    return render_template("post.html", post=post, comments=comments)


@app.route("/new_comment", methods=["POST"])
def new_comment():
    content = request.form["content"]
    post_id = request.form["post_id"]
    user_id = session.get("user_id")

    forum.add_comment(content, post_id, user_id)
    return redirect("/post/" + str(post_id))
