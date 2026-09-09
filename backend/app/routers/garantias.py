from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Garantia, Patrimonio, Movimentacao, Fornecedor
from app.schemas.garantia import (
    GarantiaCreate, GarantiaOut, GarantiaUpdate, GarantiaRetorno, SITUACOES_GARANTIA,
)
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

PERFIS_GARANTIA = ("Administrador", "Engenharia Clínica")

router = APIRouter(prefix="/patrimonios/{patrimonio_id}/garantias", tags=["Garantia"])


def _montar_saida(g: Garantia) -> dict:
    dados = GarantiaOut.model_validate(g).model_dump()
    dados["fornecedor_nome"] = g.fornecedor.razao_social if g.fornecedor else None
    return dados


def _obter_patrimonio_ou_404(patrimonio_id: int, db: Session) -> Patrimonio:
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")
    return patrimonio


@router.get("", response_model=list[GarantiaOut])
def listar(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    _obter_patrimonio_ou_404(patrimonio_id, db)
    registros = (
        db.query(Garantia)
        .options(joinedload(Garantia.fornecedor))
        .filter(Garantia.patrimonio_id == patrimonio_id)
        .order_by(Garantia.id.desc())
        .all()
    )
    return [_montar_saida(g) for g in registros]


@router.post("", response_model=GarantiaOut, status_code=201)
def criar(
    patrimonio_id: int,
    dados: GarantiaCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_GARANTIA)),
):
    if dados.situacao not in SITUACOES_GARANTIA:
        raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES_GARANTIA}")
    _obter_patrimonio_ou_404(patrimonio_id, db)
    if dados.fornecedor_id and not db.query(Fornecedor).filter(Fornecedor.id == dados.fornecedor_id).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")

    nova = Garantia(patrimonio_id=patrimonio_id, **dados.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _montar_saida(nova)


@router.put("/{garantia_id}", response_model=GarantiaOut)
def atualizar(
    patrimonio_id: int,
    garantia_id: int,
    dados: GarantiaUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_GARANTIA)),
):
    registro = (
        db.query(Garantia)
        .filter(Garantia.id == garantia_id, Garantia.patrimonio_id == patrimonio_id)
        .first()
    )
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro de garantia não encontrado.")

    dados_alterados = dados.model_dump(exclude_unset=True)
    if dados_alterados.get("situacao") and dados_alterados["situacao"] not in SITUACOES_GARANTIA:
        raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES_GARANTIA}")
    if dados_alterados.get("fornecedor_id") and not db.query(Fornecedor).filter(
        Fornecedor.id == dados_alterados["fornecedor_id"]
    ).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")

    for campo, valor in dados_alterados.items():
        setattr(registro, campo, valor)

    db.commit()
    db.refresh(registro)
    return _montar_saida(registro)


@router.post("/{garantia_id}/retorno", response_model=GarantiaOut)
def registrar_retorno(
    patrimonio_id: int,
    garantia_id: int,
    dados: GarantiaRetorno,
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_GARANTIA)),
):
    """
    Botão 'REGISTRAR RETORNO DA GARANTIA' (seção 17). O destino é escolhido
    pelo usuário (ex: Engenharia Clínica ou direto para o setor de origem).
    Cria automaticamente a movimentação Fornecedor -> destino, e vincula essa
    movimentação à garantia. A garantia já enviada não pode ser "retornada" de novo.
    """
    garantia = (
        db.query(Garantia)
        .options(joinedload(Garantia.fornecedor))
        .filter(Garantia.id == garantia_id, Garantia.patrimonio_id == patrimonio_id)
        .first()
    )
    if garantia is None:
        raise HTTPException(status_code=404, detail="Registro de garantia não encontrado.")

    if garantia.situacao == "Retornado":
        raise HTTPException(status_code=400, detail="Esta garantia já teve o retorno registrado.")

    origem = garantia.fornecedor.razao_social if garantia.fornecedor else "Fornecedor"

    movimentacao = Movimentacao(
        patrimonio_id=patrimonio_id,
        tipo="Retorno de garantia",
        origem=origem,
        destino=dados.destino,
        responsavel_id=usuario.id,
        motivo=f"Retorno da garantia #{garantia.id}" + (f" — {garantia.motivo}" if garantia.motivo else ""),
        observacao=dados.observacao,
    )
    db.add(movimentacao)
    db.flush()  # garante que movimentacao.id já existe antes de vincular

    garantia.situacao = "Retornado"
    garantia.movimentacao_retorno_id = movimentacao.id

    db.commit()
    db.refresh(garantia)
    return _montar_saida(garantia)
