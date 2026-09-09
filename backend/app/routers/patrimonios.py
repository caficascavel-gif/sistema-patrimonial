from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Patrimonio, Item, Empenho, Aquisicao, Fornecedor, Secretaria, Setor, Local, Usuario
from app.schemas.patrimonio import PatrimonioCreate, PatrimonioOut, PatrimonioUpdate, SITUACOES
from app.schemas.usuario import UsuarioLogado
from app.utils.auditoria import registrar_alteracoes_patrimonio
from app.utils.pendencias import montar_saida_patrimonio
from app.utils.permissoes import exigir_perfis, obter_usuario_atual

# Perfis que podem cadastrar/completar um patrimônio (cadastro é sempre parcial e colaborativo)
PERFIS_QUE_EDITAM_PATRIMONIO = (
    "Administrador", "Patrimônio", "Administrativo/Compras", "Engenharia Clínica",
)

router = APIRouter(prefix="/patrimonios", tags=["Patrimônios"])


def _validar_fks_patrimonio(db: Session, dados: dict):
    """
    Valida a existência de toda chave estrangeira opcional antes de gravar.
    Sem isso, um ID inválido só falharia (feio, com 500) no banco de produção —
    no SQLite usado em testes locais, sequer daria erro, porque o SQLite não
    aplica FOREIGN KEY por padrão.
    """
    verificacoes = [
        ("aquisicao_id", Aquisicao, "Aquisição informada não existe."),
        ("empenho_id", Empenho, "Empenho informado não existe."),
        ("secretaria_id", Secretaria, "Secretaria informada não existe."),
        ("setor_id", Setor, "Setor informado não existe."),
        ("local_id", Local, "Local informado não existe."),
        ("responsavel_id", Usuario, "Responsável informado não existe."),
    ]
    for campo, model, mensagem in verificacoes:
        valor = dados.get(campo)
        if valor and not db.query(model).filter(model.id == valor).first():
            raise HTTPException(status_code=400, detail=mensagem)


def _query_base(db: Session):
    """Carrega os relacionamentos usados na exibição/busca em poucas consultas (evita N+1)."""
    return db.query(Patrimonio).options(
        joinedload(Patrimonio.item),
        joinedload(Patrimonio.local),
        joinedload(Patrimonio.setor),
        joinedload(Patrimonio.empenho),
        joinedload(Patrimonio.aquisicao).joinedload(Aquisicao.fornecedor),
        joinedload(Patrimonio.aquisicao).joinedload(Aquisicao.empenho),
    )


@router.get("", response_model=list[PatrimonioOut])
def listar(
    busca: str | None = None,
    apenas_incompletos: bool = False,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    """
    Busca por patrimônio, equipamento, IPM, empenho, fornecedor ou número de série,
    conforme a tela principal do sistema (campo de pesquisa único).
    """
    query = _query_base(db)

    if busca:
        termo = f"%{busca}%"
        query = (
            query
            .outerjoin(Item, Patrimonio.item_id == Item.id)
            .outerjoin(Empenho, Patrimonio.empenho_id == Empenho.id)
            .outerjoin(Aquisicao, Patrimonio.aquisicao_id == Aquisicao.id)
            .outerjoin(Fornecedor, Aquisicao.fornecedor_id == Fornecedor.id)
            .filter(
                (Patrimonio.numero_patrimonio.like(termo))
                | (Patrimonio.ipm.like(termo))
                | (Patrimonio.numero_serie.like(termo))
                | (Item.descricao.like(termo))
                | (Empenho.numero.like(termo))
                | (Fornecedor.razao_social.like(termo))
                | (Fornecedor.nome_fantasia.like(termo))
            )
        )

    resultados = [montar_saida_patrimonio(p) for p in query.order_by(Patrimonio.numero_patrimonio).all()]
    if apenas_incompletos:
        resultados = [r for r in resultados if r["status_cadastro"] == "incompleto"]
    return resultados


@router.get("/{patrimonio_id}", response_model=PatrimonioOut)
def obter(
    patrimonio_id: int,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(obter_usuario_atual),
):
    patrimonio = _query_base(db).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")
    return montar_saida_patrimonio(patrimonio)


@router.post("", response_model=PatrimonioOut, status_code=201)
def criar(
    dados: PatrimonioCreate,
    db: Session = Depends(get_db),
    _: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_EDITAM_PATRIMONIO)),
):
    if dados.situacao_atual not in SITUACOES:
        raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES}")

    item = db.query(Item).filter(Item.id == dados.item_id).first()
    if item is None:
        raise HTTPException(status_code=400, detail="Equipamento (item) informado não existe.")

    _validar_fks_patrimonio(db, dados.model_dump())

    existente = db.query(Patrimonio).filter(Patrimonio.numero_patrimonio == dados.numero_patrimonio).first()
    if existente:
        raise HTTPException(status_code=400, detail="Já existe um patrimônio com esse número.")

    novo = Patrimonio(**dados.model_dump())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return montar_saida_patrimonio(novo)


@router.put("/{patrimonio_id}", response_model=PatrimonioOut)
def atualizar(
    patrimonio_id: int,
    dados: PatrimonioUpdate,
    db: Session = Depends(get_db),
    usuario: UsuarioLogado = Depends(exigir_perfis(*PERFIS_QUE_EDITAM_PATRIMONIO)),
):
    """
    Usado tanto para completar um cadastro parcial (ex: setor administrativo
    adicionando fornecedor/NE depois) quanto para editar dados já existentes.
    Cada campo alterado gera uma linha de auditoria (seção 25).
    """
    patrimonio = db.query(Patrimonio).filter(Patrimonio.id == patrimonio_id).first()
    if patrimonio is None:
        raise HTTPException(status_code=404, detail="Patrimônio não encontrado.")

    dados_alterados = dados.model_dump(exclude_unset=True)
    if "situacao_atual" in dados_alterados and dados_alterados["situacao_atual"] is not None:
        if dados_alterados["situacao_atual"] not in SITUACOES:
            raise HTTPException(status_code=400, detail=f"Situação inválida. Use uma de: {SITUACOES}")

    _validar_fks_patrimonio(db, dados_alterados)

    valores_antes = {campo: getattr(patrimonio, campo) for campo in dados_alterados}

    for campo, valor in dados_alterados.items():
        setattr(patrimonio, campo, valor)

    registrar_alteracoes_patrimonio(db, usuario.id, patrimonio_id, valores_antes, dados_alterados)

    db.commit()
    db.refresh(patrimonio)
    return montar_saida_patrimonio(patrimonio)
