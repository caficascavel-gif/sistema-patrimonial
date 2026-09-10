"""
Configurador único do Sistema de Controle Patrimonial.

Faz tudo isso, sozinho, quando você dá 2 cliques nele (ou no .exe gerado):
  1. Inicializa o MySQL portátil, se ainda não foi inicializado.
  2. Liga o MySQL (se ainda não estiver ligado).
  3. Define a senha do root e cria o usuário do sistema (patrimonio_app).
  4. Cria o banco de dados e todas as tabelas (a partir do schema.sql).
  5. Gera o arquivo backend/.env sozinho, já com uma chave secreta aleatória.
  6. Pergunta nome/usuário/senha e cria o primeiro Administrador.

Você só responde 3 perguntas (nome, usuário, senha do Administrador) —
todo o resto roda sozinho. Não precisa saber nada de MySQL nem digitar
nenhum outro comando.

Pressupõe a estrutura de pastas do guia (GUIA_UNICO.md):
  C:\\PatrimonioPortatil\\mysql\\      (MySQL portátil já extraído + my.ini)
  C:\\PatrimonioPortatil\\api\\        (onde este configurador coloca o .env)
"""
import getpass
import secrets
import subprocess
import sys
import time
from pathlib import Path

try:
    import pymysql
    import bcrypt
except ImportError:
    print("ERRO: faltam bibliotecas. Rode primeiro: pip install pymysql bcrypt")
    input("Pressione Enter para sair...")
    sys.exit(1)

PASTA_BASE = Path("C:/PatrimonioPortatil")
PASTA_MYSQL = PASTA_BASE / "mysql"
PASTA_API = PASTA_BASE / "api"
MY_INI = PASTA_MYSQL / "my.ini"
DADOS_MYSQL = PASTA_MYSQL / "data"
PORTA_MYSQL = 3307

# Ajuste aqui se o schema.sql não estiver ao lado deste arquivo quando você
# rodar direto do zip (o .exe gerado já embute o schema.sql junto — ver o
# spec do PyInstaller).
if getattr(sys, "frozen", False):
    CAMINHO_SCHEMA = Path(sys._MEIPASS) / "schema.sql"
else:
    CAMINHO_SCHEMA = Path(__file__).resolve().parent / "schema.sql"


def passo(titulo):
    print()
    print(f"=== {titulo} ===")


def inicializar_mysql_se_necessario():
    passo("Verificando o MySQL")
    ja_inicializado = DADOS_MYSQL.exists() and any(DADOS_MYSQL.iterdir())
    if ja_inicializado:
        print("MySQL já foi inicializado antes — pulando essa parte.")
        return

    print("Primeira vez rodando — inicializando o MySQL (isso demora um pouco)...")
    mysqld = PASTA_MYSQL / "bin" / "mysqld.exe"
    resultado = subprocess.run(
        [str(mysqld), f"--defaults-file={MY_INI}", "--initialize-insecure", "--console"],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        print("ERRO ao inicializar o MySQL:")
        print(resultado.stderr)
        input("Pressione Enter para sair...")
        sys.exit(1)
    print("MySQL inicializado com sucesso.")


def mysql_esta_rodando(porta=None):
    porta = porta or PORTA_MYSQL
    try:
        conexao = pymysql.connect(host="127.0.0.1", port=porta, user="root", password="", connect_timeout=2)
        conexao.close()
        return True
    except pymysql.err.OperationalError as erro:
        # "Access denied" (1045) significa que o servidor ESTÁ rodando, só a
        # senha que não é mais vazia (rodamos isso antes) — nesse caso
        # também consideramos "rodando" pros fins desta checagem.
        return erro.args[0] == 1045


def detectar_mysql_ja_ativo():
    """
    Procura um MySQL já rodando e pronto pra uso: primeiro na porta que o
    projeto usa por padrão (3307), depois na porta padrão do MySQL (3306).
    Isso cobre o caso de já existir um serviço de MySQL rodando na máquina
    (às vezes instalado como serviço do Windows, ex.: "patrimonioMySQL267")
    antes mesmo do configurador rodar — nesse caso não faz sentido abrir
    OUTRO mysqld.exe por cima; só usamos o que já está no ar.
    """
    for porta in (PORTA_MYSQL, 3306):
        if mysql_esta_rodando(porta):
            return porta
    return None


def ligar_mysql_se_necessario():
    global PORTA_MYSQL
    passo("Verificando se o MySQL está ligado")

    porta_ativa = detectar_mysql_ja_ativo()
    if porta_ativa is not None:
        if porta_ativa != PORTA_MYSQL:
            print(f"Já existe um MySQL rodando na porta {porta_ativa} nesta máquina")
            print("(provavelmente um serviço já instalado) — vamos usar ele em vez de abrir outro.")
            PORTA_MYSQL = porta_ativa
        else:
            print("MySQL já está rodando.")
        return

    print("Ligando o MySQL em segundo plano...")
    mysqld = PASTA_MYSQL / "bin" / "mysqld.exe"
    subprocess.Popen(
        [str(mysqld), f"--defaults-file={MY_INI}", "--console"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    for _ in range(30):
        time.sleep(1)
        if mysql_esta_rodando():
            print("MySQL no ar.")
            return
    print("ERRO: o MySQL não respondeu depois de 30 segundos.")
    print("Se já existe outro MySQL ou XAMPP rodando nesta máquina, feche-o e tente de novo.")
    input("Pressione Enter para sair...")
    sys.exit(1)


def configurar_usuarios_do_banco():
    passo("Configurando usuários do banco de dados")

    senha_root = secrets.token_urlsafe(16)
    senha_app = secrets.token_urlsafe(16)

    try:
        conexao = pymysql.connect(host="127.0.0.1", port=PORTA_MYSQL, user="root", password="")
        print("Definindo senha do root e criando o usuário do sistema...")
        with conexao.cursor() as cursor:
            cursor.execute(f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{senha_root}'")
            cursor.execute(f"CREATE USER IF NOT EXISTS 'patrimonio_app'@'%' IDENTIFIED BY '{senha_app}'")
            # Contas "anônimas" (usuário em branco) que alguns instaladores deixam por
            # padrão podem interceptar o login de QUALQUER usuário nomeado vindo de
            # 'localhost' — removemos por segurança, mesmo que não devessem existir.
            cursor.execute("DELETE FROM mysql.user WHERE User = ''")
            cursor.execute("FLUSH PRIVILEGES")
        conexao.commit()
        conexao.close()
    except pymysql.err.OperationalError as erro:
        if erro.args[0] == 1045:
            print("Usuários já estavam configurados de uma vez anterior — pulando essa parte.")
            print("(Se você perdeu a senha gerada anteriormente, apague a pasta")
            print(f" '{DADOS_MYSQL}' inteira e rode este configurador de novo do zero.)")
            return None, None
        raise

    return senha_root, senha_app


def salvar_senhas_geradas(senha_root, senha_app):
    if senha_app is None:
        return  # nada novo foi gerado nesta execução
    arquivo = PASTA_BASE / "SENHAS_GERADAS_NAO_PERDER.txt"
    conteudo = (
        "Senhas geradas automaticamente pelo configurador do Sistema de Controle Patrimonial.\n"
        "Guarde este arquivo em local seguro (ele NÃO é necessário no dia a dia do sistema,\n"
        "só se precisar mexer diretamente no banco de dados no futuro).\n\n"
        f"Usuário 'root' do MySQL: {senha_root}\n"
        f"Usuário 'patrimonio_app' do MySQL: {senha_app}\n"
    )
    arquivo.write_text(conteudo, encoding="utf-8")
    print(f"As senhas geradas foram salvas em: {arquivo}")


def carregar_schema_se_necessario(senha_root, senha_app):
    passo("Criando as tabelas do sistema")
    if senha_app is None:
        print("Pulando (banco já estava configurado de antes).")
        return

    if not CAMINHO_SCHEMA.exists():
        print(f"ERRO: não encontrei o schema.sql em {CAMINHO_SCHEMA}")
        input("Pressione Enter para sair...")
        sys.exit(1)

    texto_schema = CAMINHO_SCHEMA.read_text(encoding="utf-8")
    # remove linhas que são só comentário (começam com --) antes de dividir por ";" —
    # senão um trecho do arquivo que é só um bloco de comentário (comum entre uma
    # tabela e outra) vira um "comando" sem SQL nenhum dentro, e o MySQL recusa.
    linhas_sem_comentario = [
        linha for linha in texto_schema.splitlines() if not linha.strip().startswith("--")
    ]
    texto_schema_limpo = "\n".join(linhas_sem_comentario)

    conexao = pymysql.connect(host="127.0.0.1", port=PORTA_MYSQL, user="root", password=senha_root)
    with conexao.cursor() as cursor:
        for comando in texto_schema_limpo.split(";"):
            comando = comando.strip()
            if comando:
                cursor.execute(comando)
    conexao.commit()

    with conexao.cursor() as cursor:
        cursor.execute("GRANT ALL PRIVILEGES ON patrimonio_db.* TO 'patrimonio_app'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
    conexao.commit()
    conexao.close()
    print("Tabelas criadas com sucesso.")


def escrever_env(senha_app):
    passo("Configurando o arquivo .env da API")
    if senha_app is None:
        print("Pulando (banco já estava configurado de antes — .env não é sobrescrito).")
        return

    PASTA_API.mkdir(parents=True, exist_ok=True)
    arquivo_env = PASTA_API / ".env"
    chave_jwt = secrets.token_hex(32)
    conteudo = (
        f"DATABASE_URL=mysql+pymysql://patrimonio_app:{senha_app}@127.0.0.1:{PORTA_MYSQL}/patrimonio_db\n"
        f"JWT_SECRET_KEY={chave_jwt}\n"
        f"JWT_ALGORITHM=HS256\n"
        f"JWT_EXPIRE_MINUTES=480\n"
        f"DOCUMENTOS_DIR={PASTA_API / 'documentos'}\n"
    )
    arquivo_env.write_text(conteudo, encoding="utf-8")
    print(f"Arquivo criado em: {arquivo_env}")


def criar_primeiro_administrador(senha_app):
    passo("Criar o primeiro usuário Administrador")

    conexao = pymysql.connect(
        host="127.0.0.1", port=PORTA_MYSQL, user="patrimonio_app",
        password=senha_app or input("Senha do usuário 'patrimonio_app' (gerada numa execução anterior): "),
        database="patrimonio_db",
    )
    with conexao.cursor() as cursor:
        cursor.execute("SELECT id FROM perfis WHERE nome = 'Administrador'")
        linha = cursor.fetchone()
        if linha is None:
            print("ERRO: perfil Administrador não existe (schema.sql não foi carregado direito).")
            input("Pressione Enter para sair...")
            sys.exit(1)
        perfil_admin_id = linha[0]

        cursor.execute("SELECT COUNT(*) FROM usuarios")
        (total_usuarios,) = cursor.fetchone()
        if total_usuarios > 0:
            print("Já existe pelo menos um usuário cadastrado — pulando a criação do Administrador.")
            print("(Se quiser criar outro mesmo assim, rode este configurador de novo.)")
            conexao.close()
            return

    print("Vamos criar o primeiro usuário Administrador do sistema.")
    nome = input("Nome completo: ").strip()
    usuario_login = input("Usuário (login): ").strip()
    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")
    if senha != confirmacao:
        print("ERRO: as senhas não coincidem. Rode o configurador de novo.")
        input("Pressione Enter para sair...")
        sys.exit(1)

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with conexao.cursor() as cursor:
        cursor.execute(
            "INSERT INTO usuarios (nome, usuario, senha_hash, perfil_id, ativo) VALUES (%s, %s, %s, %s, 1)",
            (nome, usuario_login, senha_hash, perfil_admin_id),
        )
    conexao.commit()
    conexao.close()
    print(f"Administrador '{usuario_login}' criado com sucesso!")


def main():
    print("Configurador do Sistema de Controle Patrimonial")
    print("Isso só precisa ser rodado uma vez.")

    inicializar_mysql_se_necessario()
    ligar_mysql_se_necessario()
    senha_root, senha_app = configurar_usuarios_do_banco()
    salvar_senhas_geradas(senha_root, senha_app)
    carregar_schema_se_necessario(senha_root, senha_app)
    escrever_env(senha_app)
    criar_primeiro_administrador(senha_app)

    print()
    print("=== TUDO PRONTO ===")
    print("Agora é só abrir o SistemaPatrimonialAPI.exe.")
    input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()
