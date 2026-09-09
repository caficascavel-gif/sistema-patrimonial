from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

PERFIS_QUE_GERENCIAM_CADASTROS = ("Administrador", "Administrativo/Compras")


def criar_router_crud_simples(model, schema_create, schema_out, prefixo: str, tag: str) -> APIRouter:
    """
    Gera um router CRUD para cadastros simples com campos (nome, ativo).
    Usado por: categorias, marcas, secretarias.
    Consulta é liberada para qualquer usuário autenticado; escrita é restrita
    a Administrador e Administrativo/Compras (perfis que mantêm cadastros base).
    """
    router = APIRouter(prefix=prefixo, tags=[tag])

    @router.get("", response_model=list[schema_out])
    def listar(db: Session = Depends(get_db), _: UsuarioLogado = Depends(obter_usuario_atual)):
        return db.query(model).order_by(model.nome).all()

    @router.post("", response_model=schema_out, status_code=201)
    def criar(
        dados: schema_create,
        db: Session = Depends(get_db),
        _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
    ):
        existente = db.query(model).filter(model.nome == dados.nome).first()
        if existente:
            raise HTTPException(status_code=400, detail=f"Já existe um registro com o nome '{dados.nome}'.")
        novo = model(**dados.model_dump())
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    @router.put("/{item_id}", response_model=schema_out)
    def atualizar(
        item_id: int,
        dados: schema_create,
        db: Session = Depends(get_db),
        _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_GERENCIAM_CADASTROS)),
    ):
        registro = db.query(model).filter(model.id == item_id).first()
        if registro is None:
            raise HTTPException(status_code=404, detail="Registro não encontrado.")
        for campo, valor in dados.model_dump().items():
            setattr(registro, campo, valor)
        db.commit()
        db.refresh(registro)
        return registro

    return router
