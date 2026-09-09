from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth, usuarios, cadastros_simples, modelos, fornecedores, organizacao, itens,
    empenhos, aquisicoes, patrimonios, movimentacoes, manutencoes, garantias,
    anotacoes, documentos, relatorios, auditoria, pendencias, dashboard, perfis,
)

app = FastAPI(
    title="Sistema de Controle Patrimonial",
    version="0.1.0",
    description="API do sistema de controle patrimonial e equipamentos — Etapa 12 (todas as 12 etapas concluídas).",
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(cadastros_simples.router_categorias)
app.include_router(cadastros_simples.router_marcas)
app.include_router(cadastros_simples.router_secretarias)
app.include_router(modelos.router)
app.include_router(fornecedores.router)
app.include_router(organizacao.router)
app.include_router(itens.router)
app.include_router(empenhos.router)
app.include_router(aquisicoes.router)
app.include_router(patrimonios.router)
app.include_router(movimentacoes.router)
app.include_router(manutencoes.router)
app.include_router(garantias.router)
app.include_router(anotacoes.router)
app.include_router(documentos.router)
app.include_router(relatorios.router)
app.include_router(auditoria.router)
app.include_router(pendencias.router)
app.include_router(dashboard.router)
app.include_router(perfis.router)


@app.get("/", tags=["Status"])
def status_api():
    return {"status": "online", "etapa_atual": "12 - todas as etapas concluídas"}


# A tela web (Etapa 4 da versão zero-custo) fica em /app — de propósito, não em "/",
# pra não conflitar com o status da API acima (usado pela página porteira pra saber
# se o sistema está no ar). O JS da tela web chama a API com caminhos absolutos
# (ex: "/auth/login"), então funciona tudo na mesma origem, sem CORS e sem precisar
# configurar endereço de servidor nenhum.
_PASTA_ESTATICA = Path(__file__).resolve().parent / "static"
if _PASTA_ESTATICA.exists():
    app.mount("/app", StaticFiles(directory=str(_PASTA_ESTATICA), html=True), name="frontend")
