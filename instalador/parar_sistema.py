"""
Encerra as 3 partes do sistema (MySQL, API, Cloudflare Tunnel) de uma vez,
sem abrir nenhuma janela.
"""
import subprocess
import time
from pathlib import Path

LOG = Path(__file__).resolve().parent / "parar.log"
PROCESSOS = ["cloudflared.exe", "SistemaPatrimonialAPI.exe", "mysqld.exe"]

CREATE_NO_WINDOW = 0x08000000


def registrar(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")
    except Exception:
        pass


def main():
    registrar("=== Encerrando o Sistema de Controle Patrimonial ===")
    for nome in PROCESSOS:
        subprocess.run(
            ["taskkill", "/IM", nome, "/F"],
            capture_output=True,
            creationflags=CREATE_NO_WINDOW,
        )
        registrar(f"Encerrado: {nome}")
    registrar("Tudo encerrado.")


if __name__ == "__main__":
    main()
