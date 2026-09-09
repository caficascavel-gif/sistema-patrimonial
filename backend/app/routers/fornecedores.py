from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Fornecedor
from app.schemas.cadastros import FornecedorCreate, FornecedorOut, FornecedorUpdate
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])


@router.get("", response_model=list[FornecedorOut])
def listar(
    busca: str | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Fornecedor)
    if busca:
        termo = f"%{busca}%"
        query = query.filter(
            (Fornecedor.razao_social.like(termo))
            | (Fornecedor.nome_fantasia.like(termo))
            | (Fornecedor.cnpj.like(termo))
        )
    return query.order_by(Fornecedor.razao_social).all()


@router.get("/{fornecedor_id}", response_model=FornecedorOut)
def obter(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if fornecedor is None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
    return fornecedor


@router.post("", response_model=FornecedorOut, status_code=201)
def criar(
    dados: FornecedorCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    if dados.cnpj:
        existente = db.query(Fornecedor).filter(Fornecedor.cnpj == dados.cnpj).first()
        if existente:
            raise HTTPException(status_code=400, detail="Já existe um fornecedor com esse CNPJ.")
    novo = Fornecedor(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{fornecedor_id}", response_model=FornecedorOut)
def atualizar(
    fornecedor_id: int,
    dados: FornecedorUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if fornecedor is None:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado.")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(fornecedor, campo, valor)
    db.commit()
    db.refresh(fornecedor)
    return fornecedor
