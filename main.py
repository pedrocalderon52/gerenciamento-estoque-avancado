import sqlite3
import bcrypt
import os
import sys
import datetime
from time import sleep



conexao = sqlite3.connect('estoque.db')
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(255) UNIQUE NOT NULL,
        quantidade INTEGER NOT NULL,
        preco FLOAT(10, 2) NOT NULL 
               )
               

""")
conexao.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nome_usuario VARCHAR(32) UNIQUE NOT NULL, 
               senha VARCHAR(52) NOT NULL,
               permissao VARCHAR(6) CHECK (permissao IN ('admin', 'leitor', 'editor')) NOT NULL
               );


""")
conexao.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acao TEXT NOT NULL, 
        usuario TEXT NOT NULL,
        data TEXT NOT NULL,
        hora TEXT NOT NULL
        );
""")

permissoes = {'admin': range(1, 8), 'editor': range(1, 7), 'leitor': {2, 5, 6}}

def loading():
    for _ in range(135):
        print(".", end="")
        sleep(0.05)
    print("\n\n")

def input_dados(modo, adm = False):
    match modo:
        case 'c':
            while True:
                nome = input("Digite o nome do seu produto:\n")
                if len(nome) <= 255:
                    break
                else:
                    print("Nome muito longo! Digite um nome de 0 a 255 caracteres")

            while True:
                try:
                    quantidade = int(input(f"Digite a quantidade de {nome}:\n"))
                    break
                except:
                    print("erro, insira um número válido")

            while True:
                try:
                    preco = float(input(f"Digite o preco de {nome}:\n"))
                    break
                except:
                    print("erro, insira um preco válido")

            return nome, quantidade, preco
                
        case 'u':
            while True:
                try:
                    id = int(input(f"Digite o ID do produto que deseja atualizar:\n"))
                    break
                except:
                    print("erro, insira um ID válido")


            while True:
                nome = input("Digite o novo nome do seu produto:\n")
                if len(nome) <= 255:
                    break
                else:
                    print("Nome muito longo! Digite um nome de 0 a 255 caracteres")


            while True:
                try:
                    quantidade = int(input(f"Digite a nova quantidade de {nome}:\n"))
                    if quantidade < 0: 
                        raise Exception("Quantidade negativa")
                    break
                except:
                    print("Erro, insira uma quantidade válida")

            while True:
                try:
                    preco = float(input(f"Digite o novo preco de {nome}:\n"))
                    break
                except:
                    print("erro, insira um preco válido")

            return id, nome, quantidade, preco
        
        case 'd':
            while True:
                try:
                    id = int(input(f"Digite o ID do produto que deseja excluir:\n"))
                    break
                except:
                    print("erro, insira um ID válido")
            return id
        case 'add_usuario':
            while True:
                nome_usuario = input("Digite o nome de usuário:\n")
                if len(nome_usuario) <= 32 and len(nome_usuario) >= 6:
                    break
                else:
                    print("\nNome de usuário inválido! Escolha um nome de usuário de 6 a 32 caracteres\n")

            while True:
                senha = input(f"Digite a {'sua' if not adm else ""} senha {"do usuário" if adm else ""}:\n")
                if len(senha) <= 60 and len(senha) >= 6:
                    if input(f"Repita a {'sua' if not adm else ""} senha {"do usuário" if adm else ""}:\n") == senha:
                        break
                    else:
                        print("\nSenhas diferentes!! Tente novamente\n")
                else:
                    print("\nSenha inválida! Escolha uma senha entre 6 a 60 caracteres\n")

            if adm:
                while True:
                    permissao = input("Digite a permissão desse usuário (leitor, editor ou admin): ").lower()
                    if permissao not in {'admin', 'leitor', 'editor'}:
                        print("Digite uma permissão válida! ")
                    else:
                        break
            else:
                permissao = 'leitor'
            return nome_usuario, senha, permissao

                    
            
def adicionar_usuario(nome_usuario, adm = False):
    nome_usuario, senha, permissao = input_dados('add_usuario', adm=adm)

    senha_criptografada = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO usuarios(nome_usuario, senha, permissao)
            VALUES (?, ?, ?)
    """, (nome_usuario, senha_criptografada, permissao))
        adicionar_log("Adicionar usuário", nome_usuario)
    except sqlite3.IntegrityError:
        print("\nUsuário já existente no sistema. ")
    
    conexao.commit()





def inserir_produto():
    nome, quantidade, preco = input_dados('c')
    try:
        cursor.execute(f"""
            INSERT INTO produtos(nome, quantidade, preco)
            VALUES
            (?, ?, ?);
                        """, (nome, quantidade, preco, ))
        
        conexao.commit()

    except sqlite3.IntegrityError:
        print("\nProduto já existente no sistema. \n")


def listar_produtos():
    cursor.execute("SELECT * FROM produtos")
    print("\n\n\n" + "-" * 133)
    print(f"| {"ID":^30} | {"Produto":^30} | {"Preço":^30} | {"Quantidade":^30} |")
    print("-" * 133)
    for produto in cursor.fetchall():
        print(f"| {produto[0]:^30} | {produto[1]:^30} | {f'R$ {produto[3]:.2f}'.replace('.', ','):^30} | {produto[2]:^30} |")
    print("-" * 133)
    
    input("\nPressione enter para voltar ao menu principal")
    conexao.commit()


def listar_usuarios():
    cursor.execute("SELECT * FROM usuarios")
    print("\n\n\n" + "-" * 112)
    print(f"| {"ID":^32} | {"Nome":^55} | {"Permissão":^15} |")
    print("-" * 112)
    for dados_usuario in cursor.fetchall():
        print(f"| {dados_usuario[0]:^32} | {dados_usuario[1]:^55} | {dados_usuario[3]:^15} |")
    print("-" * 112)
    
    input("\nPressione enter para voltar ao menu principal")
    conexao.commit()


def pesquisar_produto_nome():
    texto = input("Digite o nome do produto: ")
    cursor.execute(f"SELECT * FROM produtos WHERE nome LIKE '%{texto}%'")
    lista_produtos_achados = cursor.fetchall()
    try:
        int(lista_produtos_achados[0][0]) # verifica se o ID do primeiro valor é um número inteiro, se não, é porque é NULL, logo, não existem valores

        print("\n\n\n" + "-" * 133)
        print(f"| {"ID":^30} | {"Produto":^30} | {"Preço":^30} | {"Quantidade":^30} |")
        print("-" * 133)
        for produto in lista_produtos_achados():
            print(f"| {produto[0]:^30} | {produto[1]:^30} | {f'R$ {produto[3]:.2f}'.replace('.', ','):^30} | {produto[2]:^30} |")
        print("-" * 133)

    except:
        print("\nNenhum produto foi encontrado.")
    
    del lista_produtos_achados

    input("\nPressione enter para voltar ao menu principal")



def atualizar_produto():
    """
    Atualiza os dados de um produto no banco de dados, pelo ID
    """

    id, novo_nome, nova_quantidade, novo_preco = input_dados('u') # tratar caso de id não encontrado ANTES de pedir nome, preço, quantidade

    cursor.execute(f"""UPDATE produtos SET nome = ?, quantidade = ?, preco = ? WHERE id = ?""", (novo_nome, nova_quantidade, novo_preco, id))
    conexao.commit()

    if cursor.rowcount > 0:
        print("produto atualizado com sucesso")
    else:
        print("produto não encontrado")


def excluir_produto():
    id = input_dados('d')
    
    cursor.execute(f"DELETE FROM produtos WHERE id = ?", (id, )) # tratar caso de id não encontrado
    conexao.commit()


def excluir_usuario():
    try:
        id = int(input("Digite o id do usuário que deseja excluir:\n"))
    except:
        print("ID não encontrado! Retornando...")
        return
    
    cursor.execute(f"SELECT id, nome_usuario FROM usuarios WHERE id = ?", (id, ))
    dados_usuario = cursor.fetchone()
    conexao.commit()
    
    if dados_usuario and id != 1:
        nome_usuario = dados_usuario[1]
        confirmacao = (f"Tem certeza que deseja excluir {nome_usuario} do sistema? (y/n)\n")
        if confirmacao == 'y':
            cursor.execute(f"DELETE FROM usuarios WHERE id = ?", (id, ))
            conexao.commit()
        

def adicionar_log(acao, usuario):
    data_acao = datetime.datetime.now()
    data = data_acao.strftime("%d/%m/%Y")
    hora = data_acao.strftime("%H:%M:%S")

    cursor.execute("INSERT INTO logs(acao, usuario, data, hora) VALUES (?, ?, ?, ?);", (acao, usuario, data, hora))
    conexao.commit()


def area_do_admin(nome_usuario):
    adm = True
    while True:
        try:
            resp = int(input("""\n\n\n
                    * * * ÁREA DO ADMINISTRADOR * * *
                    
                    Digite o número correspondente à ação que deseja realizar:\n\n
        1. Adicionar usuário
        2. Ver tabela de usuários
        3. Remover Usuário
        4. Ver tabela de logs       
        5. Voltar ao menu principal            
                            
            """))
            break
        except:
            print("\n\nDigite um número válido!!\n\n")
        
    match resp:
        case 1:
            adicionar_usuario(nome_usuario, adm=adm)
            
            
        case 2:
            adicionar_log("Listar usuários", nome_usuario)
            listar_usuarios()
        case 3:
            adicionar_log("Excluir usuário", nome_usuario)
            excluir_usuario()
        case 4:
            adicionar_log("Ver tabela de logs", nome_usuario)
            ...
        case 5:
            return
        case _:
            print("Digite uma opção válida!!")
    

def main() -> None:

    os.system('cls')
    # criar uma tela inicial bonitinha
    print("*" * 133, "\n\nSISTEMA DE GERENCIAMENTO DE ESTOQUE", "\nBem vindo (a)\n\n", "*" * 133, sep="")

    nome_usuario = input("Digite o nome do seu usuário: \n")
    senha = input("\n" + "*" * 133 + "\n\nDigite sua senha: \n")
    print("*" * 133)

    cursor.execute("""
        SELECT senha, permissao FROM usuarios WHERE nome_usuario = ?
""", (nome_usuario, ))
    
    registro = cursor.fetchone()
    conexao.commit()

    if registro:
        senha_criptografada, permissao = registro
        if bcrypt.checkpw(senha.encode(), senha_criptografada):
            login = True
            print(f"Bem vindo, {nome_usuario}! Login concluído com sucesso!")
        else:
            print("Senha incorreta!")
    else:
        resp = input("Usuário não encontrado! Deseja fazer um cadastro?: \n1. Sim\n2. Não, sair")
        match resp:
            case 1:
                adicionar_usuario()
            case 2:
                login = False


    while login:
        try:
            resp: int = int(input("""Digite o número correspondente à ação que deseja realizar:"
            1. Adicionar produto
            2. Listar produtos
            3. Atualizar produto
            4. Excluir produto
            5. Pesquisa por nome
            6. Sair
            7. Área do administrador
        \n"""))
        except:
            resp = 0
            print("\nDigite um número válido")
        
        if resp not in permissoes[permissao]:
            print("\nVocê não tem autorização para realizar essa ação!!\n")
        else:
            match resp:
                case 1:
                    adicionar_log("Inserir produto", nome_usuario)
                    inserir_produto()
                case 2:
                    adicionar_log("Listar produtos", nome_usuario)
                    listar_produtos()
                case 3:
                    adicionar_log("Atualizar produto", nome_usuario)
                    atualizar_produto()
                case 4:
                    adicionar_log("Excluir produto", nome_usuario)
                    excluir_produto()
                case 5:
                    adicionar_log("Pesquisar produto", nome_usuario)
                    pesquisar_produto_nome()
                case 6: 
                    break
                case 7:
                    loading()
                    area_do_admin(nome_usuario)
                case _:
                    print("Digite uma opção válida")
                

    print("Tchau")


def popopop():
    senha = "C4Ldwer0NS3nh4ssecreta"
    senha_criptografada = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    cursor.execute(f"""
        INSERT INTO usuarios (nome_usuario, senha, permissao)
        VALUES
        ('pedro_calderon', ?, 'admin');
    """, (senha_criptografada, ))
    conexao.commit()
          

if __name__ == "__main__":
    main()

conexao.close()
# usuario: professor_fabio
# senha: prof_fabio_senha