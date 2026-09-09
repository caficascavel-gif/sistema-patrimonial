from sqlalchemy.orm import Session

from app.models import Auditoria, Setor, Local, Secretaria, Empenho, Aquisicao, Usuario

# Nomes amigáveis para exibir na auditoria em vez do rótulo técnico do campo
NOMES_CAMPOS = {
    "ipm": "IPM",
    "numero_serie": "número de série",
    "empenho_id": "empenho/NE",
    "aquisicao_id": "aquisição",
    "secretaria_id": "secretaria",
    "setor_id": "setor",
    "local_id": "local",
    "responsavel_id": "responsável",
    "situacao_atual": "situação",
}


def _valor_legivel(db: Session, campo: str, valor):
    """Traduz IDs de chave estrangeira para um nome legível (ex: seção 25 do documento)."""
    if valor is None:
        return None
    if campo == "setor_id":
        registro = db.query(Setor).filter(Setor.id == valor).first()
        return registro.nome if registro else str(valor)
    if campo == "local_id":
        registro = db.query(Local).filter(Local.id == valor).first()
        return registro.nome if registro else str(valor)
    if campo == "secretaria_id":
        registro = db.query(Secretaria).filter(Secretaria.id == valor).first()
        return registro.nome if registro else str(valor)
    if campo == "empenho_id":
        registro = db.query(Empenho).filter(Empenho.id == valor).first()
        return f"{registro.numero}/{registro.ano}" if registro else str(valor)
    if campo == "aquisicao_id":
        return f"Aquisição #{valor}"
    if campo == "responsavel_id":
        registro = db.query(Usuario).filter(Usuario.id == valor).first()
        return registro.nome if registro else str(valor)
    return str(valor)


def registrar_alteracoes_patrimonio(
    db: Session, usuario_id: int, patrimonio_id: int, valores_antes: dict, valores_depois: dict
):
    """
    Compara os valores antes/depois de um PUT em /patrimonios/{id} e grava uma
    linha de auditoria para cada campo que realmente mudou (seção 25).
    Não faz commit — a rota que chama isso já commita a transação inteira junto.
    """
    for campo, valor_novo in valores_depois.items():
        valor_antigo = valores_antes.get(campo)
        if valor_antigo == valor_novo:
            continue

        registro = Auditoria(
            usuario_id=usuario_id,
            patrimonio_id=patrimonio_id,
            entidade="patrimonio",
            entidade_id=patrimonio_id,
            acao=f"atualizar_{campo}",
            campo=NOMES_CAMPOS.get(campo, campo),
            valor_anterior=_valor_legivel(db, campo, valor_antigo),
            valor_novo=_valor_legivel(db, campo, valor_novo),
        )
        db.add(registro)
