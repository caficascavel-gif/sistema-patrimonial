"""
Liga o Sistema de Controle Patrimonial inteiro: MySQL -> API -> Túnel,
totalmente em segundo plano, SEM NENHUMA JANELA aparecendo (nem na barra
de tarefas). Importante porque este PC também é usado pra bater ponto —
qualquer janela extra corre risco de ser fechada por engano por quem só
quer bater o ponto.

Não escreve nada na tela (não tem console). Se algo der errado, o motivo
fica registrado em C:\PatrimonioPortatil\IniciarSistema\iniciar.log.
"""
import subprocess
import time
from pathlib import Path

BASE = Path("C:/PatrimonioPortatil")
LOG = Path(__file__).resolve().parent / "iniciar.log"

# Flag do Windows que impede qualquer janela de console de ser criada
# pro processo filho — é o que garante que nada aparece na barra de tarefas.
CREATE_NO_WINDOW = 0x08000000


def registrar(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")
    except Exception:
        pass


def iniciar(nome, caminho_exe, pasta_trabalho, argumentos=None):
    if not caminho_exe.exists():
        registrar(f"ERRO: não encontrei {caminho_exe} — confira se a pasta C:\\PatrimonioPortatil foi copiada certinha.")
        return
    comando = [str(caminho_exe)] + (argumentos or [])
    registrar(f"Iniciando {nome}...")
    subprocess.Popen(comando, cwd=str(pasta_trabalho), creationflags=CREATE_NO_WINDOW)


def main():
    registrar("=== Ligando o Sistema de Controle Patrimonial (modo silencioso) ===")

    iniciar(
        "MySQL", BASE / "mysql" / "bin" / "mysqld.exe", BASE / "mysql" / "bin",
        [f"--defaults-file={BASE / 'mysql' / 'my.ini'}"],
    )
    time.sleep(15)

    iniciar("API", BASE / "api" / "SistemaPatrimonialAPI.exe", BASE / "api")
    time.sleep(10)

    iniciar(
        "Cloudflare Tunnel", BASE / "cloudflare" / "cloudflared.exe", BASE / "cloudflare",
        ["tunnel", "--config", str(BASE / "cloudflare" / "config.yml"), "run", "patrimonio"],
    )

    registrar("=== Tudo iniciado, rodando em segundo plano sem janelas ===")


if __name__ == "__main__":
    main()
