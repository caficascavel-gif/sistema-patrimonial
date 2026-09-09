from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Perfil
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import obter_usuario_atual

router = APIRouter(prefix="/perfis", tags=["Perfis"])


@router.get("")
def listar(db: Session = Depends(get_db), _: UsuarioLogado = Depends(obter_usuario_atual)):
    return [{"id": p.id, "nome": p.nome} for p in db.query(Perfil).filter(Perfil.ativo.is_(True)).order_by(Perfil.nome).all()]
