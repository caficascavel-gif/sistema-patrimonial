from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item, Categoria, Marca, Modelo
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(prefix="/itens", tags=["Itens/Equipamentos"])


def _validar_fks(db: Session, dados: dict):
    if dados.get("categoria_id") and not db.query(Categoria).filter(Categoria.id == dados["categoria_id"]).first():
        raise HTTPException(status_code=400, detail="Categoria informada não existe.")
    if dados.get("marca_id") and not db.query(Marca).filter(Marca.id == dados["marca_id"]).first():
        raise HTTPException(status_code=400, detail="Marca informada não existe.")
    if dados.get("modelo_id") and not db.query(Modelo).filter(Modelo.id == dados["modelo_id"]).first():
        raise HTTPException(status_code=400, detail="Modelo informado não existe.")


@router.get("", response_model=list[ItemOut])
def listar(
    busca: str | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Item)
    if busca:
        query = query.filter(Item.descricao.like(f"%{busca}%"))
    return query.order_by(Item.descricao).all()


@router.get("/{item_id}", response_model=ItemOut)
def obter(
    item_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    return item


@router.post("", response_model=ItemOut, status_code=201)
def criar(
    dados: ItemCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS, "Engenharia Clínica")),
):
    _validar_fks(db, dados.model_dump())
    novo = Item(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/{item_id}", response_model=ItemOut)
def atualizar(
    item_id: int,
    dados: ItemUpdate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS, "Engenharia Clínica")),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    dados_alterados = dados.model_dump(exclude_unset=True)
    _validar_fks(db, dados_alterados)
    for campo, valor in dados_alterados.items():
        setattr(item, campo, valor)
    db.commit()
    db.refresh(item)
    return item
