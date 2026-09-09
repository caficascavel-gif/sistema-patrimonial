from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Aquisicao, Fornecedor, Empenho
from app.schemas.empenho_aquisicao import AquisicaoCreate, AquisicaoOut, AquisicaoUpdate
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/aquisicoes", tags=["Aquisições"])


@router.get("", response_model=list[AquisicaoOut])
def listar(db: Session = Depends(get_db), _: UsuarioLogado = Depends(obter_usuario_atual)):
    return db.query(Aquisicao).order_by(Aquisicao.id.desc()).all()


@router.get("/{aquisicao_id}", response_model=AquisicaoOut)
def obter(
    aquisicao_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    aquisicao = db.query(Aquisicao).filter(Aquisicao.id == aquisicao_id).first()
    if aquisicao is None:
        raise HTTPException(status_code=404, detail="Aquisição não encontrada.")
    return aquisicao


@router.post("", response_model=AquisicaoOut, status_code=201)
def criar(
    dados: AquisicaoCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    if dados.fornecedor_id and not db.query(Fornecedor).filter(Fornecedor.id == dados.fornecedor_id).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")
    if dados.empenho_id and not db.query(Empenho).filter(Empenho.id == dados.empenho_id).first():
        raise HTTPException(status_code=400, detail="Empenho informado não existe.")

    nova = Aquisicao(**dados.model_dump())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.put("/{aquisicao_id}", response_model=AquisicaoOut)
def atualizar(
    aquisicao_id: int,
    dados: AquisicaoUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    aquisicao = db.query(Aquisicao).filter(Aquisicao.id == aquisicao_id).first()
    if aquisicao is None:
        raise HTTPException(status_code=404, detail="Aquisição não encontrada.")

    dados_alterados = dados.model_dump(exclude_unset=True)
    if dados_alterados.get("fornecedor_id") and not db.query(Fornecedor).filter(
        Fornecedor.id == dados_alterados["fornecedor_id"]
    ).first():
        raise HTTPException(status_code=400, detail="Fornecedor informado não existe.")
    if dados_alterados.get("empenho_id") and not db.query(Empenho).filter(
        Empenho.id == dados_alterados["empenho_id"]
    ).first():
        raise HTTPException(status_code=400, detail="Empenho informado não existe.")

    for campo, valor in dados_alterados.items():
        setattr(aquisicao, campo, valor)
    db.commit()
    db.refresh(aquisicao)
    return aquisicao
