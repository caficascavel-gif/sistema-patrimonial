from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Empenho, Fornecedor
from app.schemas.empenho_aquisicao import EmpenhoCreate, EmpenhoOut, EmpenhoUpdate
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/empenhos", tags=["Empenhos/NE"])


@router.get("", response_model=list[EmpenhoOut])
def listar(
    numero: str | None = None,
    ano: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Empenho)
    if numero:
        query = query.filter(Empenho.numero.like(f"%{numero}%"))
    if ano:
        query = query.filter(Empenho.ano == ano)
    return query.order_by(Empenho.ano.desc(), Empenho.numero).all()


@router.get("/{empenho_id}", response_model=EmpenhoOut)
def obter(
    empenho_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    empenho = db.query(Empenho).filter(Empenho.id == empenho_id).first()
    if empenho is None:
        raise HTTPException(status_code=404, detail="Empenho não encontrado.")
    return empenho


@router.post("", response_model=EmpenhoOut, status_code=201)
def criar(
    dados: EmpenhoCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    existente = db.query(Empenho).filter(Empenho.numero == dados.numero, Empenho.ano == dados.ano).first()
    if existente:
        raise HTTPException(status_code=400, detail="Já existe um empenho com esse número/ano.")
    if dados.fornecedor_id and not db.query(Fornecedor).filter(Fornecedor.id == dados.fornecedor_id).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")
    novo = Empenho(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{empenho_id}", response_model=EmpenhoOut)
def atualizar(
    empenho_id: int,
    dados: EmpenhoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    empenho = db.query(Empenho).filter(Empenho.id == empenho_id).first()
    if empenho is None:
        raise HTTPException(status_code=404, detail="Empenho não encontrado.")
    dados_alterados = dados.model_dump(exclude_unset=True)
    if dados_alterados.get("fornecedor_id") and not db.query(Fornecedor).filter(
        Fornecedor.id == dados_alterados["fornecedor_id"]
    ).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")
    for campo, valor in dados_alterados.items():
        setattr(empenho, campo, valor)
    db.commit()
    db.refresh(empenho)
    return empenho
