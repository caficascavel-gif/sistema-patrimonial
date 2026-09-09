"""
Ponto de entrada usado para gerar o .exe da API com o PyInstaller.

Por que isso existe: normalmente a API roda com o comando
"uvicorn app.main:app" digitado na linha de comando. Um .exe não tem como
receber esse comando — ele precisa ser um programa que já sabe, sozinho,
o que fazer ao ser executado (por exemplo, com duplo clique, ou pelo atalho
na pasta Inicializar do Windows). Este arquivo faz exatamente isso: chama o
uvicorn programaticamente, com host e porta fixos.
"""
import uvicorn

from app.main import app

if __name__ == "__main__":
    # host 0.0.0.0 = aceita conexão de qualquer computador da rede, não só desta máquina
    uvicorn.run(app, host="0.0.0.0", port=8000)
