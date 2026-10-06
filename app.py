from flask import Flask, render_template
from funcoes.dados import carregar_notebooks

app = Flask(__name__)

@app.route("/")
def inicio():
    notebooks = carregar_notebooks()

    total = len(notebooks)

    disponiveis = sum(
        1 for notebook in notebooks
        if notebook["disponivel"]
    )

    locados = sum(
        1 for notebook in notebooks
        if not notebook["disponivel"]
    )

    processadores = {}

    for notebook in notebooks:
        processador = notebook["processador"]

        if processador not in processadores:
            processadores[processador] = []

        processadores[processador].append(notebook)

    return render_template(
        "estoque.html",
        notebooks=notebooks,
        total=total,
        disponiveis=disponiveis,
        locados=locados,
        processadores=processadores
    )
if __name__ == "__main__":
    app.run(debug=True)