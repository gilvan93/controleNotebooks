
notebooks = [] #local onde ficará armazenado os notebooks

def exibir_notebook(notebook):
    print(f"Patrimônio: {notebook['patrimonio']}")
    print(f"Serial: {notebook['serial']}")
    print(f"Marca: {notebook['marca']}")
    print(f"Modelo: {notebook['modelo']}")
    print(f"Memória RAM: {notebook['memoria_ram']}")
    print(f"Processador: {notebook['processador']}")
    print(f"Armazenamento: {notebook['armazenamento']}")
    print(f"Referência: {notebook['referencia']}")

    if notebook["disponivel"]:
        print("Disponibilidade: Disponível")
    else:
        print("Disponibilidade: Locado")

    print("--------------------------------")

def editar_disponibilidade():

    print("\n================================")
    print("       EDITAR DISPONIBILIDADE")
    print("================================")

    encontrado = False

    identificador = input("Digite o patrimonio ou serial do notebook: ")

    for notebook in notebooks:

        if notebook["patrimonio"] == identificador or notebook["serial"] == identificador:

            encontrado = True

            print(f"\nNotebook encontrado: {notebook['modelo']}")

            if notebook["disponivel"]:
                print("Notebook disponível para locação")
            else:
                print("Notebook locado")

            print("\n1 - Marcar como disponível")
            print("2 - Marcar como locado")

            opcao = input("Escolha: ")

            if opcao == "1":
                notebook["disponivel"] = True

            elif opcao == "2":
                notebook["disponivel"] = False

            else:
                print("Opção inválida!")
                return

            print("\nDisponibilidade alterada com sucesso!")
            return

    if not encontrado:
        print("\nNotebook não encontrado.")


def buscar_notebooks():
    print("\n================================")
    print("       BUSCAR NOTEBOOKS")
    print("================================")
    encontrado = False
    identificador = input("Digite serial ou patrimonio do notebook: ")

    for notebook in notebooks:
        if identificador == notebook["patrimonio"] or identificador == notebook["serial"]:
            exibir_notebook(notebook)
            encontrado = True
    if not encontrado:
        print("\nNotebook não encontrado")

def listar_notebooks():
    print("\n================================")
    print("       NOTEBOOKS CADASTRADOS")
    print("================================")

    if not notebooks:
        print("\nNenhum notebook encontrado")
        return

    for notebook in notebooks:
        exibir_notebook(notebook)
        print("---------------------------------")


def cadastrar_notebooks(): #função de cadastro dos notebooks
    print("\nCadastro de notebook")

    patrimonio = input("Patrimônio: ")
    for notebook in notebooks:
        if notebook["patrimonio"] == patrimonio:
            print("\nEquipamento ja cadastrado")
            return

    serial = input("Serial: ")
    for notebook in notebooks:
        if notebook["serial"] == serial:
            print("\n equipamento ja cadastrado")
            return

    marca = input("Marca: ")
    modelo = input("Modelo: ")
    #disponivel = input("Disponivel: ")
    memoria_ram = input("RAM: ")
    processador = input("Procesador: ")
    armazenamento = input("Armazenamento: ")
    referencia = input("Referencia: ")


    notebook = {
        "patrimonio": patrimonio,
        "serial": serial,
        "marca": marca,
        "modelo": modelo,
        "disponivel": True,
        "memoria_ram": memoria_ram,
        "processador": processador,
        "armazenamento": armazenamento,
        "referencia": referencia
    }
    notebooks.append(notebook)
    print("\nNotebook cadastrado:")


while True:
    print("================================")
    print("   CONTROLE DE NOTEBOOKS")
    print("================================")

    print("1 - Cadastrar notebook")
    print("2 - Listar notebooks")
    print("3 - buscar notebook")
    print("4 - editar disponibilidade do notebook")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        cadastrar_notebooks()

    elif opcao == "2":
        listar_notebooks()

    elif opcao == "3":
        buscar_notebooks()

    elif opcao == "4":
        editar_disponibilidade()

    elif opcao == "0":
        print("Encerrando o programa...")
        break

print(notebooks)