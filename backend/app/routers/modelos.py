from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Modelo, Marca
from app.schemas.cadastros import ModeloCreate, ModeloOut
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/modelos", tags=["Modelos"])


@router.get("", response_model=list[ModeloOut])
def listar(
    marca_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Modelo)
    if marca_id is not None:
        query = query.filter(Modelo.marca_id == marca_id)
    return query.order_by(Modelo.nome).all()


@router.post("", response_model=ModeloOut, status_code=201)
def criar(
    dados: ModeloCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    marca = db.query(Marca).filter(Marca.id == dados.marca_id).first()
    if marca is None:
        raise HTTPException(status_code=400, detail="Marca informada não existe.")
    novo = Modelo(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{modelo_id}", response_model=ModeloOut)
def atualizar(
    modelo_id: int,
    dados: ModeloCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    registro = db.query(Modelo).filter(Modelo.id == modelo_id).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Modelo não encontrado.")
    for campo, valor in dados.model_dump().items():
        setattr(registro, campo, valor)
    db.commit()
    db.refresh(registro)
    return registro
