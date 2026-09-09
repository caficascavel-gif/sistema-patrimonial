from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Anotacao, Patrimonio
from app.schemas.anotacao import AnotacaoCreate, AnotacaoOut
from app.schemas.usuario import UsuarioLogado
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

# Mesma regra de quem pode editar o patrimônio — anotação é parte do acompanhamento dele.
PERFIS_QUE_ANOTAM = ("Administrador", "Patrimônio", "Administrativo/Compras", "Engenharia Clínica")

router = APIRouter(prefix="/patrimonios/{patrimonio_id}/anotacoes", tags=["Anotações"])


def _montar_saida(a: Anotacao) -> dict:
    dados = AnotacaoOut.model_validate(a).model_dump()
    dados["usuario_nome"] = a.usuario.nome if a.usuario else None
    return dados


@router.get("", response_model=list[AnotacaoOut])
def listar(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    anotacoes = (
        db.query(Anotacao)
        .options(joinedload(Anotacao.usuario))
        .filter(Anotacao.patrimonio_id == patrimonio_id)
        .order_by(Anotacao.data_hora.desc(), Anotacao.id.desc())
        .all()
    )
    return [_montar_saida(a) for a in anotacoes]


@router.post("", response_model=AnotacaoOut, status_code=201)
def criar(
    patrimonio_id: int,
    dados: AnotacaoCreate,
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_ANOTAM)),
):
    """
    Só cria — não existe rota de editar ou apagar anotação, por design
    (seção 18: 'as anotações não devem ser simplesmente sobrescritas').
    """
    if not dados.texto.strip():
        raise HTTPException(status_code=400, detail="O texto da anotação não pode estar vazio.")

    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    nova = Anotacao(patrimonio_id=patrimonio_id, usuario_id=usuario.id, texto=dados.texto.strip())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return _montar_saida(nova)
