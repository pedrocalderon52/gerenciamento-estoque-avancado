import sqlite3
import bcrypt 

conexao = sqlite3.connect('estoque.db')
cursor = conexao.cursor()
espacamento = 30 * " "

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
                    print("Nome de usuário inválido! Escolha um nome de usuário de 6 a 32 caracteres")

            while True:
                senha = input(f"Digite a {'sua' if not adm else ""} senha {"do usuário" if adm else ""}:\n")
                if len(senha) <= 60 and len(senha) >= 6:
                    if input(f"Repita a {'sua' if not adm else ""} senha {"do usuário" if adm else ""}:\n") == senha:
                        break
                    else:
                        print("Senhas diferentes!! Tente novamente")
                else:
                    print("Senha inválida! Escolha uma senha entre 6 a 60 caracteres")

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

                    
            
def adicionar_usuario():
    nome_usuario, senha, permissao = input_dados('add_usuario', adm=True)

    senha_criptografada = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO usuarios(nome_usuario, senha, permissao)
            VALUES (?, ?, ?)
    """, (nome_usuario, senha_criptografada, permissao))
    except sqlite3.IntegrityError:
        print("\nUsuário já existente no sistema. ")





def inserir_produto():
    nome, quantidade, preco = input_dados('c')
    try:
        cursor.execute(f"""
            INSERT INTO produtos(nome, quantidade, preco)
            VALUES
            ('{nome}', '{quantidade}', {preco});
                        """)
        
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
    
    input("\n Pressione enter para voltar ao menu principal")
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

    cursor.execute(f"""UPDATE produtos SET nome = '{novo_nome}', quantidade = '{nova_quantidade}', preco = {novo_preco} WHERE id = {id}""")
    conexao.commit()

    if cursor.rowcount > 0:
        print("produto atualizado com sucesso")
    else:
        print("produto não encontrado")


def excluir_produto():
    id = input_dados('d')
    
    cursor.execute(f"DELETE FROM produtos WHERE id = {id}") # tratar caso de id não encontrado
    conexao.commit()
    

def main() -> None:

    # criar uma tela inicial bonitinha

    nome_usuario = input("Digite o nome do seu usuário: \n")
    senha = input("Digite sua senha: \n")

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


    while login:
        try:
            resp = int(input("""Digite o número correspondente à ação que deseja realizar:"
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
        
        match resp:
            case 1:
                inserir_produto()
            case 2:
                listar_produtos()
            case 3:
                atualizar_produto()
            case 4:
                excluir_produto()
            case 5:
                pesquisar_produto_nome()
            case 6: 
                break
            case 7:
                adicionar_usuario()
            case _:
                print("Digite uma opção válida")
            
    print("Tchau")

    conexao.close()

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

# usuario: professor_fabio
# senha: prof_fabio_senha