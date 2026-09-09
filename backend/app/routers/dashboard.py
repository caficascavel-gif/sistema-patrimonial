from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Patrimonio
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import obter_usuario_atual

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumo")
def resumo_dashboard(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Indicadores da tela inicial (seção 26): PATRIMÔNIOS | EM USO | MANUTENÇÃO | GARANTIA | SEM LOCAL | BAIXADOS."""
    total = db.query(Patrimonio).count()
    em_uso = db.query(Patrimonio).filter(Patrimonio.situacao_atual == "Em uso").count()
    em_manutencao = db.query(Patrimonio).filter(Patrimonio.situacao_atual == "Em manutenção").count()
    em_garantia = db.query(Patrimonio).filter(Patrimonio.situacao_atual == "Em garantia").count()
    sem_local = db.query(Patrimonio).filter(Patrimonio.local_id.is_(None)).count()
    baixados = db.query(Patrimonio).filter(
        Patrimonio.situacao_atual.in_(["Baixado", "Descartado"])
    ).count()

    return {
        "total": total,
        "em_uso": em_uso,
        "em_manutencao": em_manutencao,
        "em_garantia": em_garantia,
        "sem_local": sem_local,
        "baixados": baixados,
    }
