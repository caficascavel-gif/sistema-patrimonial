"""
Encerra as 3 partes do sistema (MySQL, API, Cloudflare Tunnel) de uma vez.
Programa de verdade — funciona mesmo com o CMD bloqueado.
"""
import subprocess

PROCESSOS = ["cloudflared.exe", "SistemaPatrimonialAPI.exe", "mysqld.exe"]


def main():
    print("=== Encerrando o Sistema de Controle Patrimonial ===")
    for nome in PROCESSOS:
        print(f"Encerrando {nome}...")
        subprocess.run(["taskkill", "/IM", nome, "/F"], capture_output=True)
    print()
    print("Tudo encerrado.")
    input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()
