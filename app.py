from flask import Flask, abort
from flask import redirect, render_template, request, session
import config, db, forum, users
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    query = request.args.get("query")
    if query:
        results = forum.search(query)
        return render_template("index.html", query=query, results=results, posts=None)
    posts = forum.get_posts()
    count = len(posts)
    return render_template(
        "index.html", count=count, posts=posts, query=None, results=[]
    )


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

    error = forum.create_user(username, password_hash)
    if error:
        return error

    return "Tunnus luotu"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = forum.get_user(username)
    if not user:
        return "VIRHE: väärä tunnus tai salasana"

    user_id = user[0]
    password_hash = user[1]

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
    require_login()
    return render_template("new.html")


@app.route("/send", methods=["POST"])
def send():
    require_login()
    title = request.form["title"]
    content = request.form["content"]
    if not title or len(title) > 100 or len(content) > 5000:
        abort(403)
    user_id = session.get("user_id")

    post_id = forum.add_post(title, content, user_id)
    return redirect("/post/" + str(post_id))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = forum.get_post(post_id)
    if not post:
        abort(404)
    comments = forum.get_comments(post_id)
    return render_template("post.html", post=post, comments=comments)


@app.route("/new_comment", methods=["POST"])
def new_comment():
    require_login()

    content = request.form["content"]
    post_id = request.form["post_id"]
    user_id = session["user_id"]

    post = forum.get_post(post_id)
    if not post:
        abort(404)

    error = forum.add_comment(content, user_id, post_id)
    if error:
        return error
    return redirect("/post/" + str(post_id))


@app.route("/edit/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    require_login()

    comment = forum.get_comment(comment_id)
    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", comment=comment)

    if request.method == "POST":
        content = request.form["content"]
        forum.update_comment(comment_id, content)
        return redirect("/post/" + str(comment["post_id"]))


@app.route("/remove/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()

    comment = forum.get_comment(comment_id)
    if comment["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", comment=comment)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_comment(comment["id"])
        return redirect("/post/" + str(comment["post_id"]))


@app.route("/edit_post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    require_login()

    post = forum.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit.html", post=post)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        if not title or len(title) > 100 or len(content) > 5000:
            abort(403)
        forum.update_post(post_id, title, content)
        return redirect("/post/" + str(post_id))


@app.route("/remove_post/<int:post_id>", methods=["GET", "POST"])
def remove_post(post_id):
    require_login()

    post = forum.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove.html", post=post)

    if request.method == "POST":
        if "continue" in request.form:
            forum.remove_post(post_id)
            return redirect("/")
        return redirect("/post/" + str(post_id))


def require_login():
    if "user_id" not in session:
        abort(403)


@app.route("/search")
def search():
    query = request.args.get("query")
    results = forum.search(query) if query else []
    return render_template("search.html", query=query, results=results)


@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    posts = users.get_posts(user_id)
    comments = users.get_comments(user_id)
    return render_template("user.html", user=user, posts=posts, comments=comments)
