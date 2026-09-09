from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Patrimonio, Aquisicao
from app.schemas.usuario import UsuarioLogado
from app.utils.pendencias import calcular_pendencias
from app.utils.permissoes import obter_usuario_atual

router = APIRouter(prefix="/pendencias", tags=["Pendências"])


@router.get("/resumo")
def resumo_pendencias(
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """
    Contagens rápidas para a visão de pendências (seção 24), ex:
    '⚠ 18 patrimônios sem fornecedor'. Clicar num item, no cliente, abre a
    listagem filtrada em /patrimonios?apenas_incompletos=true.
    """
    patrimonios = (
        db.query(Patrimonio)
        .options(
            joinedload(Patrimonio.setor), joinedload(Patrimonio.local),
            joinedload(Patrimonio.aquisicao).joinedload(Aquisicao.fornecedor),
        )
        .all()
    )

    sem_fornecedor = sem_ne = sem_localizacao = sem_numero_serie = 0
    for p in patrimonios:
        pendencias = calcular_pendencias(p)
        if "Fornecedor não informado" in pendencias or "Aquisição não vinculada" in pendencias:
            sem_fornecedor += 1
        if "NE não informado" in pendencias:
            sem_ne += 1
        if "Localização não informada" in pendencias:
            sem_localizacao += 1
        if "Número de série não informado" in pendencias:
            sem_numero_serie += 1

    aquisicoes_sem_patrimonio = (
        db.query(Aquisicao)
        .filter(~Aquisicao.id.in_(
            db.query(Patrimonio.aquisicao_id).filter(Patrimonio.aquisicao_id.isnot(None))
        ))
        .count()
    )

    return {
        "patrimonios_sem_fornecedor": sem_fornecedor,
        "patrimonios_sem_ne": sem_ne,
        "patrimonios_sem_localizacao": sem_localizacao,
        "patrimonios_sem_numero_serie": sem_numero_serie,
        "aquisicoes_sem_patrimonio": aquisicoes_sem_patrimonio,
    }
