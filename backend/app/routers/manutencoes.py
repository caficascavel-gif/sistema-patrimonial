from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Manutencao, Patrimonio, Fornecedor
from app.schemas.manutencao import (
    ManutencaoCreate, ManutencaoOut, ManutencaoUpdate, SITUACOES_MANUTENCAO,
)
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

PERFIS_MANUTENCAO = ("Administrador", "Engenharia Clínica")

router = APIRouter(prefix="/patrimonios/{patrimonio_id}/manutencoes", tags=["Manutenção"])


def _montar_saida(m: Manutencao) -> dict:
    dados = ManutencaoOut.model_validate(m).model_dump()
    dados["responsavel_nome"] = m.responsavel.nome if m.responsavel else None
    dados["fornecedor_nome"] = m.fornecedor.razao_social if m.fornecedor else None
    return dados


def _obter_patrimonio_ou_404(patrimonio_id: int, db: Session) -> Patrimonio:
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")
    return patrimonio


@router.get("", response_model=list[ManutencaoOut])
def listar(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    _obter_patrimonio_ou_404(patrimonio_id, db)
    registros = (
        db.query(Manutencao)
        .options(joinedload(Manutencao.responsavel), joinedload(Manutencao.fornecedor))
        .filter(Manutencao.patrimonio_id == patrimonio_id)
        .order_by(Manutencao.data.desc(), Manutencao.id.desc())
        .all()
    )
    return [_montar_saida(m) for m in registros]


@router.post("", response_model=ManutencaoOut, status_code=201)
def criar(
    patrimonio_id: int,
    dados: ManutencaoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_MANUTENCAO)),
):
    if dados.situacao not in SITUACOES_MANUTENCAO:
        raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES_MANUTENCAO}")
    _obter_patrimonio_ou_404(patrimonio_id, db)
    if dados.fornecedor_id and not db.query(Fornecedor).filter(Fornecedor.id == dados.fornecedor_id).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")

    nova = Manutencao(patrimonio_id=patrimonio_id, responsavel_id=usuario.id, **dados.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _montar_saida(nova)


@router.put("/{manutencao_id}", response_model=ManutencaoOut)
def atualizar(
    patrimonio_id: int,
    manutencao_id: int,
    dados: ManutencaoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_MANUTENCAO)),
):
    """Usado para evoluir a situação (ex: Em análise -> Em manutenção -> Resolvido) e registrar conclusão."""
    registro = (
        db.query(Manutencao)
        .filter(Manutencao.id == manutencao_id, Manutencao.patrimonio_id == patrimonio_id)
        .first()
    )
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro de manutenção não encontrado.")

    dados_alterados = dados.model_dump(exclude_unset=True)
    if dados_alterados.get("situacao") and dados_alterados["situacao"] not in SITUACOES_MANUTENCAO:
        raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES_MANUTENCAO}")
    if dados_alterados.get("fornecedor_id") and not db.query(Fornecedor).filter(
        Fornecedor.id == dados_alterados["fornecedor_id"]
    ).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")

    for campo, valor in dados_alterados.items():
        setattr(registro, campo, valor)

    db.commit()
    db.refresh(registro)
    return _montar_saida(registro)
