from flask import Flask, url_for, redirect, render_template, request, send_file, after_this_request
from markdown_pdf import MarkdownPdf, Section
from mistralai import Mistral
import json
import os

app = Flask(__name__)

pdf = MarkdownPdf(toc_level=2, optimize=True)

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

types = {
    "record": "Génère une fiche de révision en markdown avec ces données, n'écrit pas plus que la fiche, résume ne réécrit pas tout, pas d'ouverture",
    "quotes": "Génère une fiche avec toutes les citations en markdown avec ces données, n'écrit pas plus que la fiche"
}

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

        data_link = f"./data/{folder}/{file}"

        with open(data_link, "r") as file:
            lesson = json.load(file)

        return render_template("lesson.html", subjects=subjects, subject=lesson["subject"], title=lesson["title"], contents=lesson["contents"], data_link=data_link)
    else:
        return redirect(url_for("home"))

@app.route("/ai-function", methods=["get"])
def ai_function():
    if request.method == "GET":
        type = request.args.get("type", type=str)
        data_file = request.args.get("data", type=str)

        with open(data_file, "r") as file:
            data = file.read()

        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": types[type] + "   " + data,
                },
            ]
        )

        res = chat_response.choices[0].message.content

        print(res)

        path = "result.pdf"

        pdf.add_section(Section(res[11:len(res) - 3], paper_size="A4"))
        pdf.save(path)

        return send_file(path, as_attachment=True)
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)