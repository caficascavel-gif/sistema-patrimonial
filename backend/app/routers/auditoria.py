from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Auditoria
from app.schemas.auditoria import AuditoriaOut
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


def _montar_saida(a: Auditoria) -> dict:
    dados = AuditoriaOut.model_validate(a).model_dump()
    dados["usuario_nome"] = a.usuario.nome if a.usuario else None
    dados["numero_patrimonio"] = a.patrimonio.numero_patrimonio if a.patrimonio else None
    return dados


@router.get("", response_model=list[AuditoriaOut])
def listar(
    patrimonio_id: int | None = None,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis("Administrador")),
):
    """Log de auditoria completo — visão restrita ao Administrador."""
    query = db.query(Auditoria).options(joinedload(Auditoria.usuario), joinedload(Auditoria.patrimonio))
    if patrimonio_id:
        query = query.filter(Auditoria.patrimonio_id == patrimonio_id)
    registros = query.order_by(Auditoria.data_hora.desc()).all()
    return [_montar_saida(a) for a in registros]
