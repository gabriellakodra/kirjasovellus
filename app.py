import secrets

from flask import Flask, abort, flash
from flask import redirect, render_template, request, session, make_response
import config
import forum, users
from werkzeug.security import generate_password_hash, check_password_hash
import math

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)


def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    query = request.args.get("query")
    if query:
        results = forum.search(query)
        return render_template(
            "index.html", query=query, results=results, posts=None, page=1, page_count=1
        )
    page_size = 10
    post_count = forum.get_post_count()
    page_count = math.ceil(post_count / page_size)
    page_count = max(page_count, 1)
    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    posts = forum.get_posts(page, page_size)
    count = len(posts)
    return render_template(
        "index.html",
        count=count,
        posts=posts,
        query=None,
        results=[],
        page=page,
        page_count=page_count,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        csrf_token = session.get("csrf_token")
        if not csrf_token:
            session["csrf_token"] = secrets.token_hex(16)
            csrf_token = session["csrf_token"]
        return render_template("register.html", csrf_token=csrf_token, filled={})

    check_csrf()
    username = request.form["username"]
    if len(username) > 16:
        flash("VIRHE: Tunnus saa olla enintään 16 merkkiä")
        filled = {"username": username}
        return render_template(
            "register.html", csrf_token=session["csrf_token"], filled=filled
        )

    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if len(password1) < 6:
        flash("VIRHE: Salasana pitää olla vähintään 6 merkkiä")
        filled = {"username": username}
        return render_template(
            "register.html", csrf_token=session["csrf_token"], filled=filled
        )

    if len(password1) > 16:
        flash("VIRHE: Salasana saa olla enintään 16 merkkiä")
        filled = {"username": username}
        return render_template(
            "register.html", csrf_token=session["csrf_token"], filled=filled
        )

    if password1 != password2:
        flash("VIRHE: Antamasi salasanat eivät ole samat")
        filled = {"username": username}
        return render_template(
            "register.html", csrf_token=session["csrf_token"], filled=filled
        )

    password_hash = generate_password_hash(password1)
    error = forum.create_user(username, password_hash)
    if error:
        flash(error)
        filled = {"username": username}
        return render_template(
            "register.html", csrf_token=session["csrf_token"], filled=filled
        )

    flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        csrf_token = session.get("csrf_token")
        if not csrf_token:
            session["csrf_token"] = secrets.token_hex(16)
            csrf_token = session["csrf_token"]
        return render_template(
            "login.html", csrf_token=csrf_token, next_page=request.referrer
        )

    check_csrf()
    username = request.form["username"]
    password = request.form["password"]
    next_page = request.form["next_page"]

    user = forum.get_user(username)
    if not user:
        flash("VIRHE: Väärä tunnus tai salasana")
        return redirect("/login")

    user_id = user[0]
    password_hash = user[1]

    if check_password_hash(password_hash, password):
        session["user_id"] = user_id
        session["csrf_token"] = secrets.token_hex(16)
        return redirect(next_page)
    else:
        flash("VIRHE: Väärä tunnus tai salasana")
        return render_template("login.html", next_page=next_page)


@app.route("/logout")
def logout():
    del session["user_id"]
    return redirect("/")


@app.route("/new")
def new():
    require_login()
    csrf_token = session.get("csrf_token")
    all_classes = forum.get_all_classes()
    return render_template("new.html", all_classes=all_classes, csrf_token=csrf_token)


@app.route("/send", methods=["POST"])
def send():
    require_login()
    check_csrf()
    title = request.form["title"]
    content = request.form["content"]
    if not title or len(title) > 100 or len(content) > 5000:
        abort(403)
    user_id = session.get("user_id")

    post_id = forum.add_post(title, content, user_id)

    all_classes = forum.get_all_classes()
    classes_to_save = {}
    for class_title in all_classes:
        value = request.form.get(f"class_{class_title}")
        if value:
            classes_to_save[class_title] = value
    forum.add_post_classes(post_id, classes_to_save)
    return redirect("/post/" + str(post_id))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = forum.get_post(post_id)
    if not post:
        abort(404)

    classes = forum.get_classes(post_id)
    comments = forum.get_comments(post_id)
    return render_template("post.html", post=post, classes=classes, comments=comments)


@app.route("/new_comment", methods=["POST"])
def new_comment():
    check_csrf()
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
        check_csrf()
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
        check_csrf()
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

    all_classes = forum.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in forum.get_classes(post_id):
        classes[entry["title"]] = entry["value"]
    if request.method == "GET":

        return render_template(
            "edit.html", post=post, classes=classes, all_classes=all_classes
        )

    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        content = request.form["content"]
        if not title or len(title) > 100 or len(content) > 5000:
            abort(403)
        forum.update_post(post_id, title, content)

        all_classes = forum.get_all_classes()
        classes_to_save = {}
        for class_title in all_classes:
            value = request.form.get(f"class_{class_title}")
            if value:
                classes_to_save[class_title] = value

        forum.update_post_classes(post_id, classes_to_save)
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
        check_csrf()
        if "continue" in request.form:
            forum.remove_post(post_id)
            return redirect("/")
        return redirect("/post/" + str(post_id))


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


@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        check_csrf()

        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("VIRHE: vain jpg-kuvat sallitaan")
            return redirect("/add_image")

        image = file.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: kuva saa olla enintään 100 kilotavua")
            return redirect("/add_image")

        user_id = session["user_id"]
        users.update_image(user_id, image)
        flash("Kuvan lisäys onnistui")
        return redirect("/user/" + str(user_id))


@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response
