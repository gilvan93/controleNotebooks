
from datetime import datetime
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
    atualizacoes = [
        notebook["ultima_atualizacao"]
        for notebook in notebooks
        if notebook.get("ultima_atualizacao")
    ]

    ultima_atualizacao = max(atualizacoes) if atualizacoes else None
    total = len(notebooks)

    def obter_status(notebook):
        status = notebook.get("status")

        if status in {
            "Disponível",
            "Locado",
            "Em revisão",
            "Uso interno"
        }:
            return status

        # Compatibilidade com registros antigos
        return "Disponível" if notebook.get("disponivel", False) else "Locado"

    disponiveis = sum(
        1 for notebook in notebooks
        if obter_status(notebook) == "Disponível"
    )

    locados = sum(
        1 for notebook in notebooks
        if obter_status(notebook) == "Locado"
    )

    em_revisao = sum(
        1 for notebook in notebooks
        if obter_status(notebook) == "Em revisão"
    )

    uso_interno = sum(
        1 for notebook in notebooks
        if obter_status(notebook) == "Uso interno"
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
        em_revisao=em_revisao,
        uso_interno=uso_interno,
        processadores=processadores,
        ultima_atualizacao=ultima_atualizacao
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
            "referencia": request.form["referencia"].strip(),
            "observacao": request.form.get["observacao", ""].strip()
        }

        # Adicionar à lista e salvar no JSON
        notebooks.append(novo_notebook)
        salvar_notebooks(notebooks)

        # Voltar para o dashboard
        return redirect(url_for("inicio"))

    return render_template("cadastrar.html")


@app.route("/editar/<patrimonio>", methods=["POST"])
@login_obrigatorio
def editar_notebook(patrimonio):
    notebooks = carregar_notebooks()

    notebook_encontrado = None

    for notebook in notebooks:
        if notebook["patrimonio"] == patrimonio:
            notebook_encontrado = notebook
            break

    if notebook_encontrado is None:
        flash("Notebook não encontrado.", "erro")
        return redirect(url_for("inicio"))

    # Receber os campos do formulário
    novo_patrimonio = request.form.get("patrimonio", "").strip()
    serial = request.form.get("serial", "").strip()
    marca = request.form.get("marca", "").strip()
    modelo = request.form.get("modelo", "").strip()
    processador = request.form.get("processador", "").strip()
    memoria_ram = request.form.get("memoria_ram", "").strip()
    armazenamento = request.form.get("armazenamento", "").strip()
    referencia = request.form.get("referencia", "").strip()
    status = request.form.get("status", "").strip()
    observacao = request.form.get("observacao", "").strip()

    # Validar campos obrigatórios
    if not all([
        novo_patrimonio, serial, marca, modelo,
        processador, memoria_ram, armazenamento,
        referencia, status
    ]):
        flash("Preencha todos os campos obrigatórios.", "erro")
        return redirect(url_for("inicio"))

    # Validar status
    status_validos = {
        "Disponível",
        "Locado",
        "Em revisão",
        "Uso interno"
    }

    if status not in status_validos:
        flash("Status inválido.", "erro")
        return redirect(url_for("inicio"))

    # Impedir patrimônio ou serial duplicado
    for notebook in notebooks:
        if notebook is notebook_encontrado:
            continue

        if notebook["patrimonio"] == novo_patrimonio:
            flash("Esse patrimônio já está cadastrado.", "erro")
            return redirect(url_for("inicio"))

        if notebook["serial"] == serial:
            flash("Esse número de série já está cadastrado.", "erro")
            return redirect(url_for("inicio"))

    # Atualizar os dados do notebook
    notebook_encontrado["patrimonio"] = novo_patrimonio
    notebook_encontrado["serial"] = serial
    notebook_encontrado["marca"] = marca
    notebook_encontrado["modelo"] = modelo
    notebook_encontrado["processador"] = processador
    notebook_encontrado["memoria_ram"] = memoria_ram
    notebook_encontrado["armazenamento"] = armazenamento
    notebook_encontrado["referencia"] = referencia
    notebook_encontrado["status"] = status
    notebook_encontrado["disponivel"] = status == "Disponível"
    notebook_encontrado["observacao"] = observacao

    # Registrar data e hora da alteração
    notebook_encontrado["ultima_atualizacao"] = datetime.now().isoformat(
        timespec="seconds"
    )

    salvar_notebooks(notebooks)

    flash("Notebook atualizado com sucesso!", "sucesso")
    return redirect(url_for("inicio"))



if __name__ == "__main__":
    app.run(host="0.0.0.0",
        port=5000,
        debug=False)
