from werkzeug.security import generate_password_hash

senha = input("Digite sua senha administrativa: ")
confirmacao = input("Digite novamente a senha: ")

if senha != confirmacao:
    print("As senhas não coincidem.")
else:
    print("\nHash gerado:\n")
    print(generate_password_hash(senha))