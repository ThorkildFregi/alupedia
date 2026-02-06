from flask import Flask, url_for, redirect, render_template, request
import json

app = Flask(__name__)

with open("./data/subjects.json", "r") as file:
    subjects = json.load(file)["subjects"]

@app.route("/")
def root_to_home():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    return render_template("home.html", subjects=subjects)

@app.route("/lesson", methods=["get"])
def lesson():
    if request.method == "GET":
        folder = request.args.get("folder", type=str)
        file = request.args.get("file", type=str)

        with open(f"./data/{folder}/{file}", "r") as file:
            lesson = json.load(file)

        return render_template("lesson.html", subjects=subjects, subject=lesson["subject"], title=lesson["title"], contents=lesson["contents"])
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)