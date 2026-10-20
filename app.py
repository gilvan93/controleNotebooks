

from funcoes.dados import carregar_notebooks, salvar_notebooks
import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash

load_dotenv()

app = Flask(__name__)

chave_secreta = os.getenv("FLASK_SECRET_KEY")

if not chave_secreta:
    raise RuntimeError(
        "FLASK_SECRET_KEY não encontrada. Confira o arquivo .env."
    )

app.config["SECRET_KEY"] = chave_secreta
app.config["SESSION_COOKIE_HTTPONLY"] = True #impede que JavaScript leia diretamente o cookie da sessão.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax" #ajuda a reduzir certos riscos de requisições entre sites.
app.config["PERMANENT_SESSION_LIFETIME"] = 1800 #define 30 minutos como duração máxima para sessões

if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "FLASK_SECRET_KEY não foi configurada no arquivo .env"
    )

csrf = CSRFProtect(app)

def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar_login(*args, **kwargs):
        if not session.get("admin_logado"):
            flash("Faça login para acessar essa funcionalidade.", "aviso")
            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return verificar_login


@app.route("/login", methods=["GET", "POST"])

def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        usuario_correto = os.getenv("ADMIN_USERNAME", "")
        hash_senha = os.getenv("ADMIN_PASSWORD_HASH", "")

        if (
            usuario == usuario_correto
            and hash_senha
            and check_password_hash(hash_senha, senha)
        ):
            session.clear()
            session.permanent = True
            session["admin_logado"] = True
            flash("Login realizado com sucesso!", "sucesso")
            return redirect(url_for("inicio"))

        flash("Usuário ou senha incorretos.", "erro")

    return render_template("login.html")


#app = Flask(__name__)
@app.route("/logout", methods=["POST"])
@login_obrigatorio
def logout():
    session.clear()
    flash("Você saiu do sistema.", "sucesso")
    return redirect(url_for("inicio"))


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


@app.route("/cadastrar", methods=["GET", "POST"])
@login_obrigatorio
def cadastrar():

    if request.method == "POST":
        notebooks = carregar_notebooks()

        patrimonio = request.form["patrimonio"].strip()
        serial = request.form["serial"].strip()

        # Validar patrimônio e serial duplicados
        for notebook in notebooks:

            if notebook["patrimonio"] == patrimonio:
                return "Erro: patrimônio já cadastrado!"

            if notebook["serial"] == serial:
                return "Erro: serial já cadastrado!"

        # Criar o novo notebook
        novo_notebook = {
            "patrimonio": patrimonio,
            "serial": serial,
            "marca": request.form["marca"].strip(),
            "modelo": request.form["modelo"].strip(),
            "disponivel": request.form["disponivel"] == "true",
            "memoria_ram": request.form["memoria_ram"].strip(),
            "processador": request.form["processador"].strip(),
            "armazenamento": request.form["armazenamento"].strip(),
            "referencia": request.form["referencia"].strip()
        }

        # Adicionar à lista e salvar no JSON
        notebooks.append(novo_notebook)
        salvar_notebooks(notebooks)

        # Voltar para o dashboard
        return redirect(url_for("inicio"))

    return render_template("cadastrar.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0",
        port=5000,
        debug=False)
