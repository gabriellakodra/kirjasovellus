from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
