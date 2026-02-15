from flask import Flask, url_for, redirect, render_template, request, send_file
from markdown_pdf import MarkdownPdf, Section
from mistralai import Mistral
import json
import os

app = Flask(__name__)

pdf = MarkdownPdf(toc_level=2, optimize=True)

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

with open("./data/example_qcm.json", "r") as file:
    qcm_example = json.load(file)

types = {
    "record": "Génère une fiche de révision en markdown avec ces données, n'écrit pas plus que la fiche, résume ne réécrit pas tout, pas d'ouverture",
    "quotes": "Génère une fiche avec toutes les citations en markdown avec ces données, n'écrit pas plus que la fiche",
    "qcm": f"Génère un qcm dans le même format que celui-ci {qcm_example} avec les données que je te donne juste après, n'écrit pas plus que le json, entre 20 questions et 50 questions, utilise LaTex pour les calculs, met la moitié de questions d'applications si le cours est sur la physique ou les mathématiques",
}

with open("./data/subjects.json", "r") as file:
    subjects = json.load(file)["subjects"]

@app.route("/")
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

        if type == "qcm":
            qcm = eval(res[7:len(res) - 3])

            return render_template("qcm.html", subjects=subjects, qcm=qcm["qcm"])
        elif type == "record" or type == "quotes":
            path = "result.pdf"

            pdf.add_section(Section(res[11:len(res) - 3], paper_size="A4"))
            pdf.save(path)

            return send_file(path, as_attachment=True)
        elif type == "exercice":
            return res
        else:
            return redirect(url_for("home"))
    else:
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)