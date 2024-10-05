from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from bson.objectid import ObjectId

# URI de conexão
uri = "mongodb+srv://biblioteca:livro123@andriel.0rikb.mongodb.net/"

# Criar novo cliente e conectar-se ao servidor
client = MongoClient(uri, server_api=ServerApi('1'))

# Definir o nome do banco de dados e das coleções
database_name = 'biblioteca'
db = client[database_name]
collection_livros = db['livros']
collection_usuarios = db['usuarios']
collection_emprestimos = db['emprestimos']


# Função para cadastrar um livro
def cadastrar_livro():
    titulo = input("Digite o título do livro: ")
    autor = input("Digite o autor do livro: ")
    ano_publicacao = input("Digite o ano de publicação: ")
    genero = input("Digite o gênero do livro: ")
    codigo_unico = input("Digite o código único do livro: ")
    quantidade = float(input("Digite a quantidade de exemplares: "))

    novo_livro = {
        "titulo": titulo,
        "autor": autor,
        "ano_publicacao": ano_publicacao,
        "genero": genero,
        "codigo_unico": codigo_unico,
        "quantidade_disponivel": quantidade
    }
    resultado = collection_livros.insert_one(novo_livro)
    print(f"Livro cadastrado com ID: {resultado.inserted_id}")


# Função para cadastrar um usuário
def cadastrar_usuario():
    nome = input("Digite o nome do usuário: ")
    email = input("Digite o e-mail do usuário: ")
    nascimento = input("Digite a data de nascimento do usuário (YYYY-MM-DD): ")
    documento = input("Digite o documento do usuário (CPF ou RG): ")

    novo_usuario = {
        "nome": nome,
        "email": email,
        "nascimento": nascimento,
        "documento": documento,
        "data_cadastro": datetime.now()
    }
    resultado = collection_usuarios.insert_one(novo_usuario)
    print(f"Usuário cadastrado com ID: {resultado.inserted_id}")


# Função para realizar um empréstimo de livro
def emprestar_livro():
    titulo = input("Digite o título do livro: ")
    documento_usuario = input("Digite o documento do usuário (CPF ou RG): ")

    livro = collection_livros.find_one({"titulo": titulo})
    usuario = collection_usuarios.find_one({"documento": documento_usuario})

    if livro and livro["quantidade_disponivel"] > 0 and usuario:
        novo_emprestimo = {
            "livro_id": livro["_id"],
            "usuario_id": usuario["_id"],
            "data_emprestimo": datetime.now(),
            "data_devolucao": None,
            "status": "pendente"
        }
        collection_emprestimos.insert_one(novo_emprestimo)
        collection_livros.update_one(
            {"_id": livro["_id"]},
            {"$inc": {"quantidade_disponivel": -1}}
        )
        print("Livro emprestado com sucesso.")
    else:
        if not livro:
            print("Livro não disponível para empréstimo ou não encontrado.")
        if not usuario:
            print("Usuário não encontrado.")


# Função para realizar a devolução de um livro
def devolver_livro():
    titulo = input("Digite o título do livro: ")
    documento_usuario = input("Digite o documento do usuário (CPF ou RG): ")

    usuario = collection_usuarios.find_one({"documento": documento_usuario})
    if not usuario:
        print("Usuário não encontrado.")
        return

    emprestimo = collection_emprestimos.find_one({
        "livro_id": {"$in": [livro["_id"] for livro in collection_livros.find({"titulo": titulo})]},
        "usuario_id": usuario["_id"],
        "status": "pendente"
    })

    if emprestimo:
        collection_emprestimos.update_one(
            {"_id": emprestimo["_id"]},
            {"$set": {"data_devolucao": datetime.now(), "status": "devolvido"}}
        )
        collection_livros.update_one(
            {"_id": emprestimo["livro_id"]},
            {"$inc": {"quantidade_disponivel": 1}}
        )
        print("Livro devolvido com sucesso.")
    else:
        print("Empréstimo não encontrado ou já devolvido.")


# Função para consultar livros disponíveis
def consultar_livros_disponiveis():
    livros_disponiveis = collection_livros.find({"quantidade_disponivel": {"$gt": 0}})
    print("Livros disponíveis:")
    for livro in livros_disponiveis:
        print(f"{livro['titulo']} - Autor: {livro['autor']} - Disponíveis: {livro['quantidade_disponivel']}")


# Função para consultar empréstimos de um usuário
def consultar_emprestimos_usuario():
    documento_usuario = input("Digite o documento do usuário (CPF ou RG): ")
    usuario = collection_usuarios.find_one({"documento": documento_usuario})

    if not usuario:
        print("Usuário não encontrado.")
        return

    emprestimos = collection_emprestimos.find({"usuario_id": usuario["_id"], "status": "pendente"})
    print(f"Empréstimos do usuário com documento {documento_usuario}:")
    for emprestimo in emprestimos:
        livro = collection_livros.find_one({"_id": emprestimo["livro_id"]})
        print(
            f"Livro: {livro['titulo']} - Data do Empréstimo: {emprestimo['data_emprestimo']} - Data prevista de devolução: {emprestimo['data_emprestimo'] + timedelta(days=14)}")


# Função para listar empréstimos vencidos
def consultar_emprestimos_vencidos():
    hoje = datetime.now()
    emprestimos_vencidos = collection_emprestimos.find({
        "data_devolucao": None,
        "data_emprestimo": {"$lt": hoje - timedelta(days=14)}
    })
    print("Empréstimos vencidos:")
    for emprestimo in emprestimos_vencidos:
        livro = collection_livros.find_one({"_id": emprestimo["livro_id"]})
        print(f"Livro: {livro['titulo']} - Data do Empréstimo: {emprestimo['data_emprestimo']}")


# Função para consultar todos os usuários cadastrados
def consultar_todos_usuarios():
    usuarios = collection_usuarios.find()
    print("Usuários cadastrados:")

    for usuario in usuarios:
        nome = usuario.get('nome', 'Não consta')
        email = usuario.get('email', 'Não consta')
        documento = usuario.get('documento', 'Não consta')
        data_cadastro = usuario.get('data_cadastro', 'Não consta')

        print(f"Nome: {nome}, E-mail: {email}, Documento: {documento}, Data de Cadastro: {data_cadastro}")

    if collection_usuarios.count_documents({}) == 0:
        print("Nenhum usuário cadastrado.")


# Função para submenu de consultas
def submenu_consulta():
    while True:
        print("+-------------------------------------+")
        print("|           MENU CONSULTA             |")
        print("+-------------------------------------+")
        print("| 1. Consultar Empréstimos de Usuário |")
        print("| 2. Consultar Livros Disponíveis     |")
        print("| 3. Consultar Empréstimos Vencidos   |")
        print("| 4. Consultar Todos os Usuários      |")
        print("| 0. Voltar ao Menu Principal         |")
        print("+-------------------------------------+")

        opcao = input("Escolha uma opção de consulta: ")

        if opcao == '1':
            consultar_emprestimos_usuario()
        elif opcao == '2':
            consultar_livros_disponiveis()
        elif opcao == '3':
            consultar_emprestimos_vencidos()
        elif opcao == '4':
            consultar_todos_usuarios()
        elif opcao == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# Função para submenu de cadastro
def submenu_cadastro():
    while True:
        print("+-----------------------------------+")
        print("|           MENU CADASTRO           |")
        print("+-----------------------------------+")
        print("| 1. Cadastrar Livro                |")
        print("| 2. Cadastrar Usuário              |")
        print("| 0. Voltar ao Menu Principal       |")
        print("+-----------------------------------+")

        opcao = input("Escolha uma opção de cadastro: ")

        if opcao == '1':
            cadastrar_livro()
        elif opcao == '2':
            cadastrar_usuario()
        elif opcao == '0':
            break
        else:
            print("Opção inválida. Tente novamente.")


# Menu principal
def menu_principal():
    while True:
        print("+-----------------------------------+")
        print("|         MENU PRINCIPAL            |")
        print("+-----------------------------------+")
        print("| 1. Cadastrar                      |")
        print("| 2. Emprestar Livro                |")
        print("| 3. Devolver Livro                 |")
        print("| 4. Consultar                      |")
        print("| 0. Sair                           |")
        print("+-----------------------------------+")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            submenu_cadastro()
        elif opcao == '2':
            emprestar_livro()
        elif opcao == '3':
            devolver_livro()
        elif opcao == '4':
            submenu_consulta()
        elif opcao == '0':
            print("Saindo do sistema.")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu_principal()
