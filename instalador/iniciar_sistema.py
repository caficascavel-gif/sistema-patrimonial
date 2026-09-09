"""
Liga o Sistema de Controle Patrimonial inteiro: MySQL -> API -> Túnel, nessa
ordem, com uma pausa entre cada um. Diferente de um arquivo .bat, este é um
programa de verdade — funciona mesmo em computadores onde o Prompt de
Comando (CMD) está bloqueado.
"""
import subprocess
import sys
import time
from pathlib import Path

BASE = Path("C:/PatrimonioPortatil")


def iniciar(nome, caminho_exe, pasta_trabalho, argumentos=None):
    if not caminho_exe.exists():
        print(f"ERRO: não encontrei {caminho_exe}")
        print("Confira se a pasta C:\\PatrimonioPortatil foi copiada certinha.")
        input("Pressione Enter para sair...")
        sys.exit(1)
    comando = [str(caminho_exe)] + (argumentos or [])
    print(f"Iniciando {nome}...")
    subprocess.Popen(comando, cwd=str(pasta_trabalho), creationflags=subprocess.CREATE_NEW_CONSOLE)


def main():
    print("=== Ligando o Sistema de Controle Patrimonial ===")
    print()

    iniciar(
        "MySQL", BASE / "mysql" / "bin" / "mysqld.exe", BASE / "mysql" / "bin",
        [f"--defaults-file={BASE / 'mysql' / 'my.ini'}", "--console"],
    )
    print("Aguardando o MySQL terminar de subir (15 segundos)...")
    time.sleep(15)

    iniciar("API", BASE / "api" / "SistemaPatrimonialAPI.exe", BASE / "api")
    print("Aguardando a API terminar de subir (10 segundos)...")
    time.sleep(10)

    iniciar(
        "Cloudflare Tunnel", BASE / "cloudflare" / "cloudflared.exe", BASE / "cloudflare",
        ["tunnel", "--config", str(BASE / "cloudflare" / "config.yml"), "run", "patrimonio"],
    )

    print()
    print("=== Tudo iniciado! ===")
    print("3 janelas novas devem ter aberto (MySQL, API, Tunnel) — deixe todas abertas o dia todo.")
    input("Pressione Enter para fechar esta janela (as outras 3 continuam rodando normalmente)...")


if __name__ == "__main__":
    main()
