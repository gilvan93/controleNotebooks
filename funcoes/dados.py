import json

def salvar_notebooks(notebooks):
    with open("notebooks.json", "w") as arquivo:
        json.dump(notebooks, arquivo, indent=4)

def carregar_notebooks():
    try:
        with open("notebooks.json", "r") as arquivo:
            dados = json.load(arquivo)
            #print("dados carregados")
            #print(dados)

            return dados

    except json.JSONDecodeError:
        return []

    except FileNotFoundError:
        return []