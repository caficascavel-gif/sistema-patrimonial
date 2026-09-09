from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Movimentacao, Patrimonio
from app.schemas.movimentacao import MovimentacaoCreate, MovimentacaoOut, TIPOS_MOVIMENTACAO
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

# Perfis que podem registrar movimentação (a mesma regra de quem edita o patrimônio)
PERFIS_QUE_MOVIMENTAM = ("Administrador", "Patrimônio", "Engenharia Clínica")

router = APIRouter(prefix="/patrimonios/{patrimonio_id}/movimentacoes", tags=["Movimentações"])


def _montar_saida(mov: Movimentacao) -> dict:
    dados = MovimentacaoOut.model_validate(mov).model_dump()
    dados["responsavel_nome"] = mov.responsavel.nome if mov.responsavel else None
    return dados


@router.get("", response_model=list[MovimentacaoOut])
def listar(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """Retorna o histórico completo do patrimônio, mais recente primeiro (linha do tempo)."""
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    movimentacoes = (
        db.query(Movimentacao)
        .options(joinedload(Movimentacao.responsavel))
        .filter(Movimentacao.patrimonio_id == patrimonio_id)
        .order_by(Movimentacao.data.desc(), Movimentacao.id.desc())
        .all()
    )
    return [_montar_saida(m) for m in movimentacoes]


@router.post("", response_model=MovimentacaoOut, status_code=201)
def criar(
    patrimonio_id: int,
    dados: MovimentacaoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_MOVIMENTAM)),
):
    """
    Registra uma nova movimentação. NUNCA edita ou remove movimentações
    já existentes — histórico é sempre 'append only' (seção 14/32).
    O responsável é sempre o usuário logado (não é informado pelo cliente).
    """
    if dados.tipo not in TIPOS_MOVIMENTACAO:
        raise HTTPException(status_code=400, detail=f"Tipo inválido. Use um de: {TIPOS_MOVIMENTACAO}")

    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    nova = Movimentacao(
        patrimonio_id=patrimonio_id,
        tipo=dados.tipo,
        origem=dados.origem,
        destino=dados.destino,
        motivo=dados.motivo,
        observacao=dados.observacao,
        responsavel_id=usuario.id,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _montar_saida(nova)
