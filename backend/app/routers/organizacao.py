from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Setor, Local, Secretaria
from app.schemas.cadastros import SetorCreate, SetorOut, LocalCreate, LocalOut
from app.schemas.usuario import UsuarioLogado
from app.utils.crud_generico import PERFIS_QUE_GERENCIAM_CADASTROS
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

router = APIRouter(tags=["Setores e Locais"])


# ---- Setores ----

@router.get("/setores", response_model=list[SetorOut])
def listar_setores(
    secretaria_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Setor)
    if secretaria_id is not None:
        query = query.filter(Setor.secretaria_id == secretaria_id)
    return query.order_by(Setor.nome).all()


@router.post("/setores", response_model=SetorOut, status_code=201)
def criar_setor(
    dados: SetorCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    secretaria = db.query(Secretaria).filter(Secretaria.id == dados.secretaria_id).first()
    if secretaria is None:
        raise HTTPException(status_code=400, detail="Secretaria informada não existe.")
    novo = Setor(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/setores/{setor_id}", response_model=SetorOut)
def atualizar_setor(
    setor_id: int,
    dados: SetorCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    registro = db.query(Setor).filter(Setor.id == setor_id).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Setor não encontrado.")
    for campo, valor in dados.model_dump().items():
        setattr(registro, campo, valor)
    db.commit()
    db.refresh(registro)
    return registro


# ---- Locais ----

@router.get("/locais", response_model=list[LocalOut])
def listar_locais(
    setor_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    query = db.query(Local)
    if setor_id is not None:
        query = query.filter(Local.setor_id == setor_id)
    return query.order_by(Local.nome).all()


@router.post("/locais", response_model=LocalOut, status_code=201)
def criar_local(
    dados: LocalCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    setor = db.query(Setor).filter(Setor.id == dados.setor_id).first()
    if setor is None:
        raise HTTPException(status_code=400, detail="Setor informado não existe.")
    novo = Local(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.put("/locais/{local_id}", response_model=LocalOut)
def atualizar_local(
    local_id: int,
    dados: LocalCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
):
    registro = db.query(Local).filter(Local.id == local_id).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    for campo, valor in dados.model_dump().items():
        setattr(registro, campo, valor)
    db.commit()
    db.refresh(registro)
    return registro
