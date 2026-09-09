from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Patrimonio, Manutencao, Garantia, Aquisicao
from app.schemas.usuario import UsuarioLogado
from app.utils.pendencias import calcular_pendencias
from app.utils.permissoes import obter_usuario_atual

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


def _query_patrimonios_com_relacionamentos(db: Session):
    return db.query(Patrimonio).options(
        joinedload(Patrimonio.item),
        joinedload(Patrimonio.setor),
        joinedload(Patrimonio.local),
        joinedload(Patrimonio.empenho),
        joinedload(Patrimonio.aquisicao).joinedload(Aquisicao.fornecedor),
        joinedload(Patrimonio.aquisicao).joinedload(Aquisicao.empenho),
    )


def _linha_patrimonio(p: Patrimonio) -> dict:
    fornecedor_nome = None
    numero_ne = None
    if p.aquisicao:
        if p.aquisicao.fornecedor:
            fornecedor_nome = p.aquisicao.fornecedor.razao_social
        if p.aquisicao.empenho:
            numero_ne = f"{p.aquisicao.empenho.numero}/{p.aquisicao.empenho.ano}"
    if numero_ne is None and p.empenho:
        numero_ne = f"{p.empenho.numero}/{p.empenho.ano}"

    return {
        "numero_patrimonio": p.numero_patrimonio,
        "equipamento": p.item.descricao if p.item else None,
        "setor": p.setor.nome if p.setor else None,
        "local": p.local.nome if p.local else None,
        "situacao": p.situacao_atual,
        "fornecedor": fornecedor_nome,
        "ne": numero_ne,
    }


@router.get("/patrimonio-geral")
def relatorio_patrimonio_geral(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Colunas: patrimônio, equipamento, setor, local, situação, fornecedor, NE (seção 27)."""
    patrimonios = _query_patrimonios_com_relacionamentos(db).order_by(Patrimonio.numero_patrimonio).all()
    return [_linha_patrimonio(p) for p in patrimonios]


@router.get("/por-setor")
def relatorio_por_setor(
    setor_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = _query_patrimonios_com_relacionamentos(db)
    if setor_id:
        query = query.filter(Patrimonio.setor_id == setor_id)
    patrimonios = query.order_by(Patrimonio.setor_id, Patrimonio.numero_patrimonio).all()
    return [_linha_patrimonio(p) for p in patrimonios]


@router.get("/por-fornecedor")
def relatorio_por_fornecedor(
    fornecedor_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = _query_patrimonios_com_relacionamentos(db)
    if fornecedor_id:
        query = query.join(Aquisicao, Patrimonio.aquisicao_id == Aquisicao.id).filter(
            Aquisicao.fornecedor_id == fornecedor_id
        )
    patrimonios = query.order_by(Patrimonio.numero_patrimonio).all()
    linhas = [_linha_patrimonio(p) for p in patrimonios]
    if fornecedor_id:
        return linhas
    # sem filtro: só retorna quem tem fornecedor, agrupável no cliente pela coluna "fornecedor"
    return [linha for linha in linhas if linha["fornecedor"]]


@router.get("/por-empenho")
def relatorio_por_empenho(
    empenho_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = _query_patrimonios_com_relacionamentos(db)
    if empenho_id:
        query = query.filter(
            (Patrimonio.empenho_id == empenho_id)
            | (Patrimonio.aquisicao.has(Aquisicao.empenho_id == empenho_id))
        )
    patrimonios = query.order_by(Patrimonio.numero_patrimonio).all()
    linhas = [_linha_patrimonio(p) for p in patrimonios]
    if empenho_id:
        return linhas
    return [linha for linha in linhas if linha["ne"]]


@router.get("/incompletos")
def relatorio_incompletos(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Patrimônios sem informações completas (mesma regra 🟢/🟡 da ficha)."""
    patrimonios = _query_patrimonios_com_relacionamentos(db).order_by(Patrimonio.numero_patrimonio).all()
    linhas = []
    for p in patrimonios:
        pendencias = calcular_pendencias(p)
        if pendencias:
            linha = _linha_patrimonio(p)
            linha["pendencias"] = "; ".join(pendencias)
            linhas.append(linha)
    return linhas


@router.get("/em-manutencao")
def relatorio_em_manutencao(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Manutenções ainda em aberto (não Resolvido nem Sem conserto)."""
    registros = (
        db.query(Manutencao)
        .options(joinedload(Manutencao.responsavel), joinedload(Manutencao.patrimonio).joinedload(Patrimonio.item))
        .filter(Manutencao.situacao.notin_(["Resolvido", "Sem conserto"]))
        .order_by(Manutencao.data.desc())
        .all()
    )
    return [
        {
            "numero_patrimonio": m.patrimonio.numero_patrimonio if m.patrimonio else None,
            "equipamento": m.patrimonio.item.descricao if m.patrimonio and m.patrimonio.item else None,
            "data": m.data.isoformat(),
            "situacao": m.situacao,
            "problema_relatado": m.problema_relatado,
            "responsavel": m.responsavel.nome if m.responsavel else None,
        }
        for m in registros
    ]


@router.get("/em-garantia")
def relatorio_em_garantia(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Garantias ainda em aberto (não Retornado nem Sem solução)."""
    registros = (
        db.query(Garantia)
        .options(joinedload(Garantia.fornecedor), joinedload(Garantia.patrimonio).joinedload(Patrimonio.item))
        .filter(Garantia.situacao.notin_(["Retornado", "Sem solução"]))
        .order_by(Garantia.id.desc())
        .all()
    )
    return [
        {
            "numero_patrimonio": g.patrimonio.numero_patrimonio if g.patrimonio else None,
            "equipamento": g.patrimonio.item.descricao if g.patrimonio and g.patrimonio.item else None,
            "fornecedor": g.fornecedor.razao_social if g.fornecedor else None,
            "situacao": g.situacao,
            "data_envio": g.data_envio.isoformat() if g.data_envio else None,
            "previsao_retorno": g.previsao_retorno.isoformat() if g.previsao_retorno else None,
        }
        for g in registros
    ]
